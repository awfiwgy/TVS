#coding=utf-8
import json, re
from urllib.parse import quote
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name, self.host = '漫蛙动漫', 'https://www.mwdm.cc'
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': self.host}

    def getName(self): return self.name
    def init(self, extend=""): pass
    def isVideoFormat(self, url): return False
    def manualVideoCheck(self): return False
    def homeContent(self, filter):
        return {'class': [{'type_id': '2', 'type_name': '国漫'}, {'type_id': '3', 'type_name': '日漫'}, {'type_id': '1', 'type_name': '番漫'}, {'type_id': '4', 'type_name': '其他'}]}

    def homeVideoContent(self): return self._parse_list(self.host)
    def categoryContent(self, tid, pg, filter, extend): return self._parse_list(f'{self.host}/list/{tid}-{pg}/', int(pg))

    def detailContent(self, ids):
        try:
            t = self.fetch(f'{self.host}/manwa/{ids[0]}/', headers=self.header).text
            title = re.search(r'title">([^<]+)</h3>', t).group(1)
            pic = re.search(r'thumb">.*?src="([^"]+)"', t, re.S).group(1)
            desc = re.search(r'description" content="([^"]+)"', t).group(1)
            tabs = re.findall(r'href="#(down\d+-\d+)"[^>]*>([^<]+)</a>', t)
            p_f, p_u = [], []
            for tid, name in tabs:
                p_f.append(name)
                it = re.findall(r'href="([^"]+)">([^<]+)</a>', re.search(f'id="{tid}"(.*?)</ul>', t, re.S).group(1))
                p_u.append("#".join([f"{n}${l}" for l, n in it]))
            return {'list': [{'vod_id': ids[0], 'vod_name': title, 'vod_pic': self.host+pic if pic.startswith('/') else pic, 'vod_content': desc, 'vod_play_from': "$$$".join(p_f), 'vod_play_url': "$$$".join(p_u)}]}
        except: return {'list': []}

    def searchContent(self, key, quick, pg=1):
        rsp = self.fetch(f"https://www.mwdm.cc/search/-------------/?wd={quote(key)}&page={pg}", headers=self.header)
        root = self.html(rsp.text)
        
        videos = []
        for item in root.xpath('//ul[@class="stui-vodlist clearfix"]/li'):
            try:
                link = item.xpath('.//a[@class="stui-vodlist__thumb lazyload"]/@href')[0]
                title = item.xpath('.//h4[@class="stui-vodlist__title"]/a/@title')[0]
                pic = item.xpath('.//a[@class="stui-vodlist__thumb lazyload"]/@data-original')[0]
                remark = item.xpath('.//span[@class="pic-text text-right"]/text()')[0]
                videos.append({
                    "vod_id": f"https://www.mwdm.cc{link}",
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remark if remark else ""
                })
            except:
                continue
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        try:
            t = self.fetch(f'{self.host}{id}', headers=self.header).text
            p = json.loads(re.search(r'player_aaaa=(.*?);', t).group(1))
            return {'parse': 0, 'url': p['url'], 'header': self.header}
        except: return {'parse': 1, 'url': f'{self.host}{id}'}

    def _parse_list(self, url, pg=1):
        try:
            t = self.fetch(url, headers=self.header).text
            v, it = [], re.findall(r'thumb lazyload.*?href="([^"]+)".*?original="([^"]+)".*?text-right">([^<]+)</span>.*?title="([^"]+)"', t, re.S)
            for h, p, r, tit in it:
                vid = re.search(r'/manwa/(\d+)/', h).group(1) if '/manwa/' in h else h
                v.append({'vod_id': vid, 'vod_name': tit, 'vod_pic': self.host+p if p.startswith('/') else p, 'vod_remarks': r.strip()})
            pc = re.search(r'num">(\d+)/(\d+)</span>', t)
            return {'list': v, 'page': pg, 'pagecount': int(pc.group(2)) if pc else pg}
        except: return {'list': []}

    def localProxy(self, param): return None
    def destroy(self): pass
