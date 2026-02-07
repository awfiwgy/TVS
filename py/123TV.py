# coding=utf-8
import json, re, urllib.parse, requests
from base.spider import Spider

class Spider(Spider):
    def getName(self): return "A123TV"
    def init(self, extend=""): pass
    def isVideoFormat(self, url): return any(fmt in url for fmt in ['.m3u8', '.mp4', '.flv', '.avi', '.mkv', '.ts'])
    def manualVideoCheck(self): return False
    def action(self, action): pass
    def destroy(self): pass
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}

    def homeContent(self, filter):
        cateManual = [{"type_id": "10", "type_name": "电影"}, {"type_id": "11", "type_name": "连续剧"}, {"type_id": "12", "type_name": "综艺"}, {"type_id": "13", "type_name": "动漫"}, {"type_id": "15", "type_name": "福利"}]
        filter_config = {
            '10': [{"key": "class", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "动作片", "v": "1001"}, {"n": "喜剧片", "v": "1002"}, {"n": "爱情片", "v": "1003"}, {"n": "科幻片", "v": "1004"}, {"n": "恐怖片", "v": "1005"}, {"n": "剧情片", "v": "1006"}, {"n": "战争片", "v": "1007"}, {"n": "纪录片", "v": "1008"}, {"n": "动漫电影", "v": "1010"}, {"n": "奇幻片", "v": "1011"}, {"n": "动画片", "v": "1013"}, {"n": "犯罪片", "v": "1014"}, {"n": "悬疑片", "v": "1016"}, {"n": "邵氏电影", "v": "1019"}, {"n": "歌舞片", "v": "1022"}, {"n": "家庭片", "v": "1024"}, {"n": "古装片", "v": "1025"}, {"n": "历史片", "v": "1026"}, {"n": "4K电影", "v": "1027"}]}],
            '11': [{"key": "class", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "国产剧", "v": "1101"}, {"n": "香港剧", "v": "1102"}, {"n": "台湾剧", "v": "1105"}, {"n": "韩国剧", "v": "1103"}, {"n": "欧美剧", "v": "1104"}, {"n": "日本剧", "v": "1106"}, {"n": "泰国剧", "v": "1108"}, {"n": "港台剧", "v": "1110"}, {"n": "日韩剧", "v": "1111"}, {"n": "海外剧", "v": "1107"}]}],
            '12': [{"key": "class", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "内地综艺", "v": "1201"}, {"n": "港台综艺", "v": "1202"}, {"n": "日韩综艺", "v": "1203"}, {"n": "欧美综艺", "v": "1204"}, {"n": "国外综艺", "v": "1205"}]}],
            '13': [{"key": "class", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "国产动漫", "v": "1301"}, {"n": "日韩动漫", "v": "1302"}, {"n": "欧美动漫", "v": "1303"}, {"n": "海外动漫", "v": "1305"}, {"n": "里番", "v": "1307"}]}],
            '15': [{"key": "class", "name": "分类", "value": [{"n": "全部", "v": ""}, {"n": "韩国情色片", "v": "1551"}, {"n": "日本情色片", "v": "1552"}, {"n": "大陆情色片", "v": "1555"}, {"n": "香港情色片", "v": "1553"}, {"n": "台湾情色片", "v": "1554"}, {"n": "美国情色片", "v": "1556"}, {"n": "欧洲情色片", "v": "1557"}, {"n": "印度情色片", "v": "1558"}, {"n": "东南亚情色片", "v": "1559"}, {"n": "其它情色片", "v": "1550"}]}]
        }
        return {'class': cateManual, 'filters': filter_config}

    def homeVideoContent(self):
        try:
            r = requests.get("https://a123tv.com/", headers=self.header, timeout=5); r.encoding = "utf-8"
            items = re.findall(r'<a class="w4-item" href="([^"]+)".*?<img.*?data-src="([^"]+)".*?<div class="t"[^>]*>([^<]+)</div>.*?<div class="i">([^<]+)</div>', r.text, re.S)
            videos = [{"vod_id": h, "vod_name": t.strip(), "vod_pic": i if i.startswith("http") else "https:"+i, "vod_remarks": s.strip()} for h, i, t, s in items]
            return {'list': videos}
        except: return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        tid = extend['class'] if 'class' in extend and extend['class'] else tid
        url = f"https://a123tv.com/t/{tid}.html" if pg == '1' else f"https://a123tv.com/t/{tid}/p{pg}.html"
        try:
            r = requests.get(url, headers=self.header, timeout=5); r.encoding = "utf-8"
            items = re.findall(r'<a class="w4-item" href="([^"]+)".*?<img.*?data-src="([^"]+)".*?<div class="s">.*?<span>([^<]+)</span>.*?<div class="t"[^>]*title="([^"]+)">.*?<div class="i">([^<]+)</div>', r.text, re.S)
            videos = [{"vod_id": h, "vod_name": t.strip(), "vod_pic": i if i.startswith("http") else "https:"+i, "vod_remarks": r.strip()} for h, i, r, t, s in items]
            pages = re.findall(r'/p(\d+)\.html"[^>]*>(\d+)</a>', r.text)
            pagecount = max([int(p[1]) for p in pages]) if pages else int(pg)
            return {'list': videos, 'page': int(pg), 'pagecount': pagecount, 'limit': len(videos), 'total': 9999}
        except: return {'list': [], 'page': 1, 'pagecount': 1}

    def searchContent(self, key, quick, pg="1"):
        url = "https://a123tv.com/s/{}.html".format(urllib.parse.quote(key)) if pg == "1" else "https://a123tv.com/s/{}/p{}.html".format(urllib.parse.quote(key), pg)
        try:
            r = requests.get(url, headers=self.header, timeout=5); r.encoding = "utf-8"
            items = re.findall(r'<a class="w4-item" href="([^"]+)".*?<img.*?data-src="([^"]+)".*?<div class="t"[^>]*>([^<]+)</div>.*?<div class="i">([^<]+)</div>', r.text, re.S)
            videos = [{"vod_id": h, "vod_name": t.strip(), "vod_pic": i.strip() if i.strip().startswith("http") else "https:"+i.strip(), "vod_remarks": s.strip()} for h, i, t, s in items]
            return {'list': videos}
        except: return {'list': []}

    def detailContent(self, array):
        url = array[0] if array[0].startswith("http") else f"https://a123tv.com{array[0]}"
        try:
            r = requests.get(url, headers=self.header, timeout=5); r.encoding = "utf-8"; html = r.text
            vod = {"vod_id": array[0], "vod_name": "", "vod_pic": "", "vod_type": "", "vod_year": "", "vod_area": "", "vod_remarks": "", "vod_actor": "", "vod_director": "", "vod_content": ""}
            tm = re.search(r'<li class="on"><h1>([^<]+)</h1></li>', html); vod['vod_name'] = tm.group(1) if tm else ""
            pm = re.search(r'data-poster="([^"]+)"', html); vod['vod_pic'] = pm.group(1) if pm else ""
            if not vod['vod_pic'].startswith("http") and vod['vod_pic']: vod['vod_pic'] = "https:" + vod['vod_pic']
            dm = re.search(r'name="description" content="(.*?)"', html)
            if dm:
                con = dm.group(1); vod['vod_content'] = con
                am = re.search(r'演员：(.*?)(。|$)', con); vod['vod_actor'] = am.group(1) if am else ""
                arm = re.search(r'地区：(.*?)(。|$)', con); vod['vod_area'] = arm.group(1) if arm else ""
                dim = re.search(r'导演：(.*?)(。|$)', con); vod['vod_director'] = dim.group(1) if dim else ""
            pf, pu = [], []
            sm = re.search(r'var pp=({.*?});', html, re.S)
            if sm:
                data = json.loads(sm.group(1)); vno = data.get('no')
                for l in data.get('la', []):
                    el = [f"第{i+1}集$/v/{vno}/{l[0]}z{i}.html" for i in range(l[2])]
                    if el: pf.append(l[1]); pu.append("#".join(el))
            vod['vod_play_from'] = "$$$".join(pf); vod['vod_play_url'] = "$$$".join(pu)
            return {"list": [vod]}
        except: return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        try:
            r = requests.get(f"https://a123tv.com{id}", headers=self.header, timeout=5); r.encoding = "utf-8"
            match = re.search(r'data-src="([^"]+)"', r.text)
            if match: return {"parse": 0, "playUrl": "", "url": match.group(1), "header": ""}
        except: pass
        return {}

    def localProxy(self, param): pass
