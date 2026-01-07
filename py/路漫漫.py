import re
import sys
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.url = 'https://www.lmm50.com'
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Referer': self.url}

    def getName(self):
        return "路漫漫动漫"

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        classes = [{'type_name': '国产动漫', 'type_id': 'guochandongman'}, {'type_name': '动态漫画', 'type_id': 'dongtaiman'}, {'type_name': '日本动漫', 'type_id': 'ribendongman'}, {'type_name': '欧美动漫', 'type_id': 'oumeidongman'}, {'type_name': '国产动画电影', 'type_id': 'guochandonghuadianying'}, {'type_name': '日本动画电影', 'type_id': 'ribendonghuadianying'}, {'type_name': '欧美动画电影', 'type_id': 'oumeidonghuadianying'}, {'type_name': '日本特摄剧', 'type_id': 'teshepian'}]
        return {'class': classes}

    def homeVideoContent(self):
        try:
            return {'list': self._parse_vod_list(self.fetch(self.url, headers=self.header).text)}
        except:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        url = f'{self.url}/type/{tid}.html' if pg == '1' else f'{self.url}/type/{tid}_{pg}.html'
        try:
            return {'list': self._parse_vod_list(self.fetch(url, headers=self.header).text), 'page': int(pg), 'pagecount': 9999, 'limit': 20, 'total': 9999}
        except:
            return {'list': []}

    def detailContent(self, ids):
        try:
            r = self.fetch(f'{self.url}/detail/{ids[0]}.html', headers=self.header).text
            vod = {'vod_id': ids[0], 'vod_name': '', 'vod_pic': '', 'vod_type': '', 'vod_year': '', 'vod_area': '', 'vod_remarks': '', 'vod_actor': '', 'vod_director': '', 'vod_content': ''}
            tm = re.search(r'<h1 class="page-title">(.*?)</h1>', r)
            if tm: vod['vod_name'] = tm.group(1)
            pm = re.search(r'class="url_img" alt=".*?" src="(.*?)"', r)
            if pm: vod['vod_pic'] = pm.group(1)
            cm = re.search(r'class="video-info-item video-info-content">(.*?)</div>', r, re.S)
            if cm: vod['vod_content'] = re.sub(r'<[^>]+>', '', cm.group(1)).strip()
            pfl = []
            for t in re.findall(r'data-dropdown-value="(.*?)"', r):
                if t not in pfl: pfl.append(t)
            purl = []
            lbs = r.split('class="module-list')
            for b in lbs[1:]:
                if 'module-blocklist' not in b: continue
                eps = []
                for h, n in re.findall(r'<a href="(/play/.*?.html)".*?<span>(.*?)</span>', b):
                    eps.append(f"{n}${self.url}{h}")
                if eps: purl.append("#".join(eps))
            diff = len(purl) - len(pfl)
            if diff > 0: pfl.extend([f"线路{len(pfl)+i+1}" for i in range(diff)])
            elif diff < 0: pfl = pfl[:len(purl)]
            vod['vod_play_from'] = "$$$".join(pfl)
            vod['vod_play_url'] = "$$$".join(purl)
            return {'list': [vod]}
        except:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            return {'list': self._parse_vod_list(self.fetch(f'{self.url}/vod/search.html?wd={key}&page={pg}', headers=self.header).text)}
        except:
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        return {'parse': 1, 'url': id, 'header': self.header}

    def localProxy(self, param):
        return None

    def destroy(self):
        pass

    def _parse_vod_list(self, html):
        v = []
        for i, t in re.findall(r'<div class="video-img-box.*?>(.*?)<h6 class="title">(.*?)</h6>', html, re.S):
            try:
                hm = re.search(r'href="/detail/(\d+).html"', i)
                if not hm: continue
                vid = hm.group(1)
                pic = ''
                sm = re.search(r'data-src="(.*?)"', i)
                if sm: pic = sm.group(1)
                else:
                    smb = re.search(r'src="(.*?)"', i)
                    if smb: pic = smb.group(1)
                rem = ''
                rm = re.search(r'class="label">(.*?)</span>', i)
                if rm: rem = rm.group(1)
                tit = ''
                tm = re.search(r'<a.*?>(.*?)</a>', t)
                if tm: tit = tm.group(1)
                v.append({'vod_id': vid, 'vod_name': tit, 'vod_pic': pic, 'vod_remarks': rem})
            except: continue
        return v
