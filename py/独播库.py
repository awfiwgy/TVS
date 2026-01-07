import sys,re,json,urllib.parse
from base.spider import Spider
class Spider(Spider):
 def __init__(self):
  self.name='独播库'
  self.host='https://www.dbku.tv'
  self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36','Referer':self.host}
  self.video_cache={}
  self.category_cache={'4':'动漫','20':'港剧','13':'陆剧','21':'短剧','1':'电影','2':'连续剧','3':'综艺','14':'台泰剧','15':'日韩剧'}
 def getName(self):return self.name
 def init(self,extend=""):pass
 def isVideoFormat(self,url):return False
 def manualVideoCheck(self):return False
 def destroy(self):pass
 def localProxy(self,param):return None
 def homeContent(self,filter):
  return{'class':[{'type_id':k,'type_name':v}for k,v in self.category_cache.items()]}
 def homeVideoContent(self):
  try:
   rsp=self.fetch(self.host,headers=self.headers)
   return{'list':self._parse_video_list(rsp.text)[:20]}
  except:return{'list':[]}
 def categoryContent(self,tid,pg,filter,extend):
  try:
   page_num=int(pg)
   if page_num==1:url=f"{self.host}/vodtype/{tid}.html"
   else:url=f"{self.host}/vodshow/{tid}--------{page_num}---.html"
   rsp=self.fetch(url,headers=self.headers)
   videos=self._parse_video_list(rsp.text)
   pagecount=self._parse_pagecount(rsp.text,tid)
   return{'list':videos,'page':page_num,'pagecount':pagecount,'limit':20,'total':len(videos)*pagecount}
  except:return{'list':[]}
 def detailContent(self,ids):
  try:
   vid=ids[0]
   url=f"{self.host}/voddetail/{vid}.html"
   rsp=self.fetch(url,headers=self.headers)
   html=rsp.text
   name=self._extract_detail(html,r'<h1[^>]*>([^<]+)</h1>')
   pic=self._extract_detail(html,r'data-original="([^"]+)"')
   content=self._extract_detail(html,r'<span[^>]*class="data"[^>]*>(.*?)</span>',default='暂无简介')
   year=self._extract_detail(html,r'年份：</span><a[^>]*>(\d+)</a>')
   area=self._extract_detail(html,r'地区：</span><a[^>]*>([^<]+)</a>')
   director=self._extract_detail(html,r'导演：</span>(.*?)</p>')
   if not director:director=self._extract_detail(html,r'导演：</span><a[^>]*>([^<]+)</a>')
   if director:director=re.sub(r'<[^>]+>','',director).strip()
   actor=self._extract_detail(html,r'主演：</span>(.*?)</p>')
   if not actor:actor=self._extract_detail(html,r'主演：</span><a[^>]*>([^<]+)</a>')
   if actor:actor=re.sub(r'<[^>]+>','',actor).strip()
   play_url=[]
   playlist_patterns=[r'<ul[^>]*class="[^"]*myui-content__list[^"]*"[^>]*>(.*?)</ul>',r'<div[^>]*class="[^"]*myui-panel_bd[^"]*"[^>]*>(.*?)</div>']
   for pattern in playlist_patterns:
    playlist_match=re.search(pattern,html,re.S)
    if playlist_match:
     episode_matches=re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',playlist_match.group(1))
     for ep_url,ep_title in episode_matches:play_url.append(f"{ep_title}${self._make_full_url(ep_url)}")
     if play_url:break
   if not play_url:
    episode_matches=re.findall(r'<a[^>]*href="([^"]+)"[^>]*title="([^"]+)"[^>]*>',html)
    for ep_url,ep_title in episode_matches:
     if '/vodplay/'in ep_url or'/play/'in ep_url:play_url.append(f"{ep_title}${self._make_full_url(ep_url)}")
   vod={'vod_id':vid,'vod_name':name,'vod_pic':pic,'vod_year':year,'vod_area':area,'vod_actor':actor if actor else"未知",'vod_director':director if director else"未知",'vod_content':content,'vod_play_from':'独播库','vod_play_url':'#'.join(play_url)if play_url else""}
   return{'list':[vod]}
  except Exception as e:return{'list':[]}
 def searchContent(self,key,quick,pg="1"):
  try:
   page_num=int(pg)
   if page_num==1:url=f"{self.host}/vodsearch/-------------.html?wd={urllib.parse.quote(key)}"
   else:url=f"{self.host}/vodsearch/{urllib.parse.quote(key)}------------{page_num}---.html"
   rsp=self.fetch(url,headers=self.headers)
   videos=self._parse_video_list(rsp.text)
   return{'list':videos,'page':page_num,'pagecount':10}
  except:return{'list':[]}
 def playerContent(self,flag,id,vipFlags):
  return{'parse':1,'url':id,'header':self.headers}
 def _parse_video_list(self,html):
  videos=[]
  pattern=r'<a[^>]*class="[^"]*myui-vodlist__thumb[^"]*"[^>]*href="/voddetail/(\d+)\.html"[^>]*title="([^"]*)"[^>]*data-original="([^"]*)"'
  for match in re.finditer(pattern,html):
   vid,name,pic=match.groups()
   remark=""
   end_pos=match.end()
   snippet=html[end_pos:end_pos+500]
   remark_match=re.search(r'<span[^>]*class="pic-text[^"]*"[^>]*>([^<]*)</span>',snippet)
   if remark_match:remark=remark_match.group(1).strip()
   videos.append({'vod_id':vid,'vod_name':name,'vod_pic':pic,'vod_remarks':remark})
  return videos
 def _parse_pagecount(self,html,tid):
  page_patterns=[r'href="/vodshow/'+re.escape(tid)+r'-+(\d+)---\.html"',r'page=(\d+)',r'(\d+)</a>\s*</li>\s*<li[^>]*><a[^>]*>下一页']
  max_page=1
  for pattern in page_patterns:
   pages=re.findall(pattern,html)
   if pages:
    try:max_page=max(max_page,max(int(p)for p in pages if p.isdigit()))
    except:pass
  return max_page
 def _extract_detail(self,html,pattern,default=''):
  match=re.search(pattern,html,re.S)
  return match.group(1).strip()if match else default
 def _make_full_url(self,url):
  if url.startswith('http'):return url
  return f"{self.host}{url}"if url.startswith('/')else f"{self.host}/{url}"