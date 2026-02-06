# coding=utf-8
import re
import json
from urllib.parse import quote
from base.spider import Spider

class Spider(Spider):
    def getName(self): return "比卡比卡"
    def init(self, extend=""): pass
    def isVideoFormat(self, url): pass
    def manualVideoCheck(self): pass

    def __init__(self):
        self.host = "https://pika.bikaq.cc"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }

    def homeContent(self, filter):
        # 根据提供的HTML硬编码分类，减少请求
        cats = [
            {'type_id': '20', 'type_name': '新片日韩'}, {'type_id': '21', 'type_name': '字幕精选'},
            {'type_id': '22', 'type_name': '短片国产'}, {'type_id': '23', 'type_name': '酥胸外露'},
            {'type_id': '24', 'type_name': '剧情强暴'}, {'type_id': '25', 'type_name': '制服扮演'},
            {'type_id': '26', 'type_name': '熟女御姐'}, {'type_id': '27', 'type_name': '无玛转载'},
            {'type_id': '28', 'type_name': '动漫卡通'}, {'type_id': '30', 'type_name': '欧美大片'}
        ]
        return {'class': cats}

    def homeVideoContent(self):
        return self.categoryContent('20', '1', False, {})

    def categoryContent(self, tid, pg, filter, extend):
        return self._get_list(f'{self.host}/vodtype/{tid}-{pg}.html')

    def searchContent(self, key, quick, pg="1"):
        return self._get_list(f'{self.host}/vodsearch/{quote(key)}----------{pg}---.html')

    def detailContent(self, ids):
        try:
            tid = ids[0]
            html = self.fetch(f'{self.host}/voddetail/{tid}.html', headers=self.headers).text
            
            # 基础信息正则提取
            name = re.search(r'hl-dc-title[^>]+>(.*?)<', html).group(1)
            pic = re.search(r'hl-item-thumb[^>]+data-original="([^"]+)"', html).group(1)
            content = re.search(r'hl-content-text"><em>(.*?)</em>', html, re.S).group(1).strip()
            year = re.search(r'年份：</em>(\d+)', html)
            
            # 播放列表提取
            play_url = ""
            play_area = re.search(r'id="hl-plays-list"(.*?)</ul>', html, re.S)
            if play_area:
                # 提取链接: /vodplay/xxxx.html -> 拼接host
                urls = re.findall(r'<a href="([^"]+)">(.*?)</a>', play_area.group(1))
                play_url = "#".join([f"{name}${self.host}{u}" for u, name in urls])

            return {'list': [{
                'vod_id': tid, 'vod_name': name, 'vod_pic': pic, 
                'vod_year': year.group(1) if year else "", 'vod_content': content,
                'vod_play_from': '在线播放', 'vod_play_url': play_url
            }]}
        except: return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        try:
            # 尝试从播放页提取 Maccms 标准播放变量 player_aaaa
            html = self.fetch(id, headers=self.headers).text
            js_data = json.loads(re.search(r'player_aaaa=({.*?});', html).group(1))
            return {'parse': 0, 'url': js_data['url'], 'header': self.headers}
        except:
            # 提取失败或非直链，开启 sniff (parse=1)
            return {'parse': 1, 'url': id, 'header': self.headers}

    def localProxy(self, param): return None

    def _get_list(self, url):
        try:
            html = self.fetch(url, headers=self.headers).text
            # 针对列表页 li 结构的紧凑正则
            # 匹配: href="/voddetail/{id}.html", title="{name}", data-original="{pic}", class="hl-pic-tag">{remark}</div>
            pattern = r'href="/voddetail/(\d+)\.html"\s+title="([^"]+)"\s+data-original="([^"]+)".*?class="hl-pic-tag">(.*?)</div>'
            items = re.findall(pattern, html, re.S)
            
            videos = [{
                'vod_id': v[0], 
                'vod_name': v[1], 
                'vod_pic': v[2], 
                'vod_remarks': v[3].strip()
            } for v in items]
            
            return {'list': videos, 'page': 1, 'pagecount': 999, 'limit': 20, 'total': 999}
        except: return {'list': []}
