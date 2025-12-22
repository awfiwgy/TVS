# -*- coding: utf-8 -*-
# by @恰逢不爱看短剧
import sys
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = '甜圈短剧'
        self.host = 'https://mov.cenguigui.cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.video_cache = {}

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        categories = ['新剧', '逆袭', '霸总', '现代言情', '打脸虐渣', '豪门恩怨', '神豪', '马甲','都市日常', '战神归来', '小人物', '女性成长', '大女主', '穿越', '都市修仙', '强者回归','亲情', '古装', '重生', '闪婚', '赘婿逆袭', '虐恋', '追妻', '天下无敌', '家庭伦理','萌宝', '古风权谋', '职场', '奇幻脑洞', '异能', '无敌神医', '古风言情', '传承觉醒','现言甜宠', '奇幻爱情', '乡村', '历史古代', '王妃', '高手下山', '娱乐圈', '强强联合','破镜重圆', '暗恋成真', '民国', '欢喜冤家', '系统', '真假千金', '龙王', '校园','穿书', '女帝', '团宠', '年代爱情', '玄幻仙侠', '青梅竹马', '悬疑推理', '皇后','替身', '大叔', '喜剧', '剧情']
        return {'class': [{'type_id': cat, 'type_name': cat} for cat in categories]}

    def homeVideoContent(self):
        return self._get_videos({'offset': '0'})

    def categoryContent(self, tid, pg, filter, extend):
        params = {'offset': str((int(pg) - 1) * 20), 'classname': tid}
        return self._get_videos(params, paginate=True)

    def detailContent(self, ids):
        try:
            bid = ids[0]
            video_info = self.video_cache.get(bid, {})
            
            if not video_info:
                video_info = self._fetch_video_info(bid)
            
            episodes = self._get_episodes(bid, video_info)
            
            vod = {
                'vod_id': bid,
                'vod_name': video_info.get('title', '甜圈短剧'),
                'vod_pic': video_info.get('cover', ''),
                'vod_content': video_info.get('video_desc', ''),
                'vod_remarks': f"共{video_info.get('episode_cnt', '0')}集",
                'vod_play_from': '甜圈短剧',
                'vod_play_url': '#'.join(episodes)
            }
            
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        params = {'name': key, 'offset': str((int(pg) - 1) * 20)}
        return self._get_videos(params)

    def playerContent(self, flag, id, vipFlags):
        try:
            url = self._get_play_url(id)
            return {'parse': 0, 'url': url, 'header': self.headers}
        except Exception:
            return {'parse': 0, 'url': ''}

    def destroy(self):
        pass

    def localProxy(self, param):
        return None

    # 辅助方法
    def _get_videos(self, params, paginate=False):
        try:
            res = self.fetch(f'{self.host}/duanju/api.php', params=params)
            data = res.json().get('data', [])
            
            videos = []
            for item in data[:20]:  # 限制20个结果
                vid = item.get('book_id') or item.get('video_id', '')
                self.video_cache[vid] = item
                
                videos.append({
                    'vod_id': vid,
                    'vod_name': item.get('title', ''),
                    'vod_pic': item.get('cover', ''),
                    'vod_remarks': f"{item.get('episode_cnt', '0')}集"
                })
            
            if paginate:
                return {'list': videos, 'page': params['offset'][0], 'pagecount': 999}
            return {'list': videos}
        except Exception:
            return {'list': []}

    def _fetch_video_info(self, bid):
        try:
            res = self.fetch(f'{self.host}/duanju/api.php', params={'book_id': bid})
            data = res.json().get('data', {})
            return data[0] if isinstance(data, list) and data else data
        except Exception:
            return {}

    def _get_episodes(self, bid, video_info):
        episodes = []
        try:
            res = self.fetch(f'{self.host}/duanju/api.php', params={'action': 'episodes', 'book_id': bid})
            data = res.json().get('data', [])
            
            for ep in data:
                title = ep.get('title', f"第{ep.get('index', 1)}集")
                vid = ep.get('video_id', '')
                if vid:
                    episodes.append(f"{title}${vid}")
        except Exception:
            pass
        
        if not episodes:
            count = int(video_info.get('episode_cnt', 1))
            for i in range(1, count + 1):
                episodes.append(f"第{i}集${bid}_{i}")
        
        return episodes or [f"播放${bid}"]

    def _get_play_url(self, vid):
        try:
            res = self.fetch(f'{self.host}/duanju/api.php', params={'video_id': vid})
            data = res.json().get('data', {})
            
            if isinstance(data, dict):
                return data.get('url', f'{self.host}/video/{vid}.m3u8')
            elif isinstance(data, list) and data:
                return data[0].get('url', f'{self.host}/video/{vid}.m3u8')
        except Exception:
            pass
        
        return f'{self.host}/video/{vid}.m3u8'