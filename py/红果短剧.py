# -*- coding: utf-8 -*-
# by @嗷呜
import re
import sys
import urllib.parse
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        pass

    def getName(self):
        return "红果短剧"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = 'https://www.hongguodj1.cc'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    # --- 基础配置数据 ---
    classes = [
        {'type_name': '电影', 'type_id': 'dianying'},
        {'type_name': '电视剧', 'type_id': 'dianshiju'},
        {'type_name': '综艺', 'type_id': 'zongyi'},
        {'type_name': '动漫', 'type_id': 'dongman'},
        {'type_name': '短剧', 'type_id': 'duanju'},
        {'type_name': '伦理片', 'type_id': 'lunlipian'}
    ]
    
    # 通用选项
    years = ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2002", "2001", "2000"]
    years_range = [{"n": "2010年代", "v": "2010,2019"}, {"n": "2000年代", "v": "2000,2009"}, {"n": "90年代", "v": "1990,1999"}, {"n": "80年代", "v": "1980,1989"}]
    areas = ["大陆", "香港", "台湾", "美国", "韩国", "日本", "泰国", "新加坡", "马来西亚", "印度", "英国", "法国", "加拿大", "西班牙", "俄罗斯", "其它"]

    # 分类定义
    cate_map = {
        'dianying': ["喜剧", "爱情", "动作", "科幻", "动画", "悬疑", "犯罪", "惊悚", "冒险", "奇幻", "恐怖", "战争", "武侠", "情色", "剧情"],
        'dianshiju': ["古装", "战争", "青春", "偶像", "喜剧", "家庭", "犯罪", "动作", "奇幻", "剧情", "历史", "经典", "乡村", "情景", "商战", "网剧", "其它", "农村", "神话", "穿越", "刑侦", "军旅", "谍战", "年代", "职场", "校园", "动画", "言情", "科幻", "热血", "悬疑", "惊悚", "恐怖", "冒险", "励志", "罪案", "歌舞", "少女", "动漫", "旅游", "时尚", "真人秀", "未知", "文艺", "抗战", "革命", "传奇", "军事", "搞笑", "预告", "音乐", "游戏", "益智", "情感", "童话", "爱情", "推理", "灾难", "近代", "脱口秀", "美食", "网络剧", "玄幻", "破案", "真人剧"],
        'zongyi': ["喜剧", "爱情", "动作", "科幻", "动画", "悬疑", "犯罪", "惊悚", "冒险", "奇幻", "恐怖", "战争", "武侠", "情色", "剧情"],
        'dongman': ["热血", "卡通", "新番", "百合", "搞笑", "国产", "电影", "情感", "科幻", "推理", "冒险", "萝莉", "校园", "动作", "机战", "运动", "战争", "少年", "少女", "社会", "原创", "亲子", "益智", "励志", "其它"],
        'duanju': ["都市", "赘婿", "战神", "古代言情", "现代言情", "历史", "脑洞", "玄幻", "电视节目", "搞笑", "网剧", "喜剧", "萌宝", "神豪", "致富", "奇幻脑洞", "超能", "强者回归", "甜宠", "励志", "豪门恩怨", "复仇", "长生", "神医", "马甲", "亲情", "小人物", "奇幻", "无敌", "现实", "重生", "闪婚", "职场商战", "穿越", "年代", "权谋", "高手下山", "悬疑", "家国情仇", "虐恋", "古装", "时空之旅", "玄幻仙侠", "欢喜冤家", "传承觉醒", "情感", "逆袭", "家庭"],
        'lunlipian': ["男同", "gay友", "女同", "性爱", "重口", "猎奇", "人兽", "人妖", "SM", "调教", "日本", "无码", "中文", "有码", "黑人", "欧美", "国产", "网红", "主播", "萝莉", "少女", "明星", "换脸", "探花", "约炮", "传媒", "伦理", "三级", "网曝", "黑料", "激情", "动漫", "VR", "视角", "解说"]
    }

    def homeContent(self, filter):
        result = {}
        result['class'] = self.classes
        
        # 动态生成 filter_config
        # 1. 基础结构：全部 + 列表值
        year_list = [{"n": "全部", "v": ""}] + [{"n": y, "v": y} for y in self.years] + self.years_range
        area_list = [{"n": "全部", "v": ""}] + [{"n": a, "v": a} for a in self.areas]
        
        filters = {}
        for tid, categories in self.cate_map.items():
            class_list = [{"n": "全部", "v": ""}] + [{"n": c, "v": c} for c in categories]
            filters[tid] = [
                {'key': 'class', 'name': '分类', 'value': class_list},
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年代', 'value': year_list}
            ]
        
        result['filters'] = filters
        try:
            rsp = self.fetch(self.host, headers=self.headers)
            data = pq(rsp.text)
            vlist = []
            for i in data('.vod-item li').items():
                vlist.append(self.parse_vod_item(i))
            result['list'] = vlist
        except:
             result['list'] = []
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        path = []
        # 按顺序拼接参数
        for key in ['class', 'area', 'year', 'letter', 'by']:
            if key in extend and extend[key]:
                path.append(f"{key}/{urllib.parse.quote(extend[key])}")
        
        path.append(f"id/{tid}")
        if pg != '1':
             path.append(f"page/{pg}")
             
        # 根据是否有筛选条件决定 URL 模式
        if len(path) == 1 and path[0] == f"id/{tid}":
             url = f'{self.host}/vod/type/id/{tid}.html'
        else:
             url = f"{self.host}/vod/show/{'/'.join(path)}.html"

        try:
            rsp = self.fetch(url, headers=self.headers)
            data = pq(rsp.text)
            vlist = []
            for i in data('.vod-item li').items():
                vlist.append(self.parse_vod_item(i))
            result['list'] = vlist
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 20
            result['total'] = 999999
        except Exception as e:
            result['list'] = []
        return result

    def detailContent(self, ids):
        try:
            url = self.host + ids[0] if ids[0].startswith('/') else ids[0]
            if not url.startswith('http'): url = f'{self.host}/{ids[0]}'
            
            rsp = self.fetch(url, headers=self.headers)
            data = pq(rsp.text)
            
            title = data('h1').text() or data('.page-header h2').text()
            pic = data('.img-thumbnail').attr('src')
            if pic and not pic.startswith('http'): pic = self.host + pic

            vod = {
                'vod_name': title,
                'vod_pic': pic,
                'vod_content': data('.text-muted').text().strip(),
                'vod_play_from': '',
                'vod_play_url': ''
            }

            play_from = []
            play_urls = []
            
            # 解析线路名称
            tabs = data('.nav-tabs li a')
            if not tabs:
                 play_from.append('默认线路')
            else:
                 play_from = [t.text() for t in tabs.items()]

            # 解析线路内容
            panes = data('.tab-content ul.playurl, .tab-content ul.tab-pane, .vod-play-list')
            for ul in panes.items():
                urls = []
                for li in ul.find('li a').items():
                    name = li.text()
                    href = li.attr('href')
                    if href: urls.append(f'{name}${href}')
                if urls: play_urls.append('#'.join(urls))

            # 数据对齐
            if play_urls:
                if len(play_from) < len(play_urls):
                    play_from.extend([f'线路{i+1}' for i in range(len(play_from), len(play_urls))])
                vod['vod_play_from'] = '$$$'.join(play_from[:len(play_urls)])
                vod['vod_play_url'] = '$$$'.join(play_urls)
            
            return {'list': [vod]}
        except:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            url = f'{self.host}/vod/search/wd/{key}.html'
            if pg != '1': url = f'{self.host}/vod/search/wd/{key}/page/{pg}.html'
            rsp = self.fetch(url, headers=self.headers)
            data = pq(rsp.text)
            vlist = [self.parse_vod_item(i) for i in data('.vod-item li').items()]
            return {'list': vlist, 'page': pg}
        except:
             return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        try:
            url = self.host + id if id.startswith('/') else id
            rsp = self.fetch(url, headers=self.headers)
            html = rsp.text
            # 优先提取直链
            m3u8 = pq(html)('div[data-play]').attr('data-play')
            if m3u8: return {'parse': 0, 'url': m3u8, 'header': self.headers}
            return {'parse': 1, 'url': url, 'header': self.headers}
        except:
            return {'parse': 1, 'url': id, 'header': self.headers}

    def localProxy(self, param):
        pass

    def parse_vod_item(self, item):
        img = item.find('img')
        pic = img.attr('data-src') or img.attr('src')
        if pic and not pic.startswith('http'):
            pic = self.host + pic if pic.startswith('/') else f'{self.host}/{pic}'
        return {
            'vod_id': item.find('a.pic').attr('href'),
            'vod_name': item.find('h3 a').text() or img.attr('alt'),
            'vod_pic': pic,
            'vod_remarks': item.find('.continu').text() or item.find('.pic-text').text()
        }
