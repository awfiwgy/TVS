# -*- coding: utf-8 -*-
import sys
import json
import re
import time
import traceback
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    # 飞流视频 API 配置
    api_host = 'https://www.flixflop.com'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.flixflop.com/',
        'Origin': 'https://www.flixflop.com',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def init(self, extend=""):
        print("[飞流视频] 初始化 - 线程池优化版")
        try:
            if extend:
                if isinstance(extend, str):
                    config = json.loads(extend)
                else:
                    config = extend
                if config.get('api_host'):
                    self.api_host = config['api_host']
        except Exception as e:
            print(f"配置初始化错误: {e}")

    def getName(self):
        return "飞流视频-Pro"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    # --- 核心逻辑区 ---

    def homeContent(self, filter):
        print("[飞流视频] 并发获取分类与筛选...")
        result = {'class': [], 'filters': {}}
        
        try:
            # 1. 获取分类列表
            cdata = self.fetch_json(f"{self.api_host}/api/v1/categories")
            if not cdata:
                return result

            # 构建分类列表
            classes = []
            for item in cdata.get('data', []):
                classes.append({
                    'type_id': str(item.get('category_id')),
                    'type_name': item.get('name')
                })
            result['class'] = classes

            # 2. 并发获取筛选条件 (参考参考代码的并发逻辑)
            # 使用线程池同时请求所有分类的筛选接口，速度提升N倍
            with ThreadPoolExecutor(max_workers=10) as executor:
                # 提交所有任务: {future: type_id}
                future_to_tid = {
                    executor.submit(self.get_filters_dynamic, cls['type_id']): cls['type_id'] 
                    for cls in classes
                }
                
                # 处理返回结果
                for future in as_completed(future_to_tid):
                    tid = future_to_tid[future]
                    try:
                        f_data = future.result()
                        if f_data:
                            result['filters'][tid] = f_data
                    except Exception as e:
                        print(f"筛选获取失败 {tid}: {e}")

        except Exception as e:
            print(f"首页异常: {e}")
            traceback.print_exc()
            
        return result

    def homeVideoContent(self):
        print("[飞流视频] 获取首页推荐...")
        # 为了保证图片质量，直接请求第一个分类（通常是电影或推荐）的数据
        # 这里硬编码取第一个分类ID可能会变，所以动态获取一下比较稳妥，或者直接写死常用ID
        # 电影ID: 151438147786375168
        return self.categoryContent("151438147786375168", 1, False, None)

    def categoryContent(self, tid, pg, filter, extend):
        """
        分类视频列表
        """
        page = int(pg) if pg else 1
        limit = 48
        
        params = {
            'page': page,
            'per_page': limit
        }
        # 合并筛选参数
        if extend:
            params.update(extend)

        url = f"{self.api_host}/api/v1/explore/{tid}?{urlencode(params)}"
        data = self.fetch_json(url)
        
        videos = []
        if data:
            videos = self.clean_vod_list(data.get('data', []))
            
            meta = data.get('meta', {})
            total = int(meta.get('count', 0))
            page_count = (total + limit - 1) // limit if limit > 0 else 1
            
            return {
                'list': videos,
                'page': page,
                'pagecount': page_count,
                'limit': limit,
                'total': total
            }
            
        return {'list': videos}

    def detailContent(self, ids):
        vid = ids[0]
        print(f"[飞流视频] 详情请求 id={vid}")
        
        # 并发请求详情和播放源 (参考代码思路，提升详情页加载速度)
        with ThreadPoolExecutor(max_workers=2) as executor:
            f_detail = executor.submit(self.fetch_json, f"{self.api_host}/api/v1/videos/{vid}")
            f_sources = executor.submit(self.fetch_json, f"{self.api_host}/api/v1/videos/{vid}/sources")
            
            d_data = f_detail.result() or {}
            s_data = f_sources.result() or {}

        info = d_data.get('data', {})
        sources_list = s_data.get('data', [])

        play_from = []
        play_url = []

        # 解析播放源
        for source in sources_list:
            s_name = source.get('name', '默认线路')
            s_url_str = source.get('url', '')
            
            if s_url_str:
                # 兼容性处理：如果API返回没有"正片$"前缀，手动补全
                if '$' not in s_url_str and '#' not in s_url_str:
                    s_url_str = f"正片${s_url_str}"
                
                play_from.append(s_name)
                play_url.append(s_url_str)

        vod = {
            'vod_id': vid,
            'vod_name': info.get('title', ''),
            'vod_pic': info.get('cover_image', ''),
            'vod_type': '',
            'vod_year': str(info.get('published_year', '')),
            'vod_area': str(info.get('area', '')),
            'vod_remarks': info.get('remarks', ''),
            'vod_actor': self.format_list(info.get('actors', [])),
            'vod_director': self.format_list(info.get('directors', [])),
            'vod_content': info.get('description', ''),
            'vod_play_from': '$$$'.join(play_from),
            'vod_play_url': '$$$'.join(play_url)
        }
        
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        print(f"[飞流视频] 搜索: {key}")
        page = int(pg) if pg else 1
        
        params = {
            'query': key,
            'rank': 0,
            'page': page
        }
        url = f"{self.api_host}/api/v1/explore/search?{urlencode(params)}"
        data = self.fetch_json(url)
        
        videos = []
        if data:
            # 搜索结果去重逻辑
            seen = set()
            raw_list = data.get('data', [])
            unique_list = []
            for item in raw_list:
                vid = str(item.get('video_id'))
                if vid not in seen:
                    seen.add(vid)
                    unique_list.append(item)
            
            videos = self.clean_vod_list(unique_list)

        return {
            'list': videos,
            'page': page
        }

    def playerContent(self, flag, id, vipFlags):
        # 飞流的API在detailContent阶段已经获取到了真实的m3u8/mp4地址
        # 所以这里直接透传即可，无需额外请求
        if id.startswith('http'):
            return {
                'parse': 0,
                'playUrl': '',
                'url': id,
                'header': self.headers
            }
        return {}

    # --- 辅助功能区 ---

    def get_filters_dynamic(self, tid):
        """单个分类筛选获取任务"""
        url = f"{self.api_host}/api/v1/explore/{tid}/filters"
        data = self.fetch_json(url)
        if not data: return []
        
        d = data.get('data', {})
        filters = []
        
        # 配置映射: (API字段, TVBox Key, 显示名称, 取值字段)
        config = [
            ('genres', 'genre', '类型', 'genre_id'),
            ('areas', 'area', '地区', 'area_id'),
            ('published_years', 'year', '年份', None), # 年份直接是值
            ('languages', 'lang', '语言', 'language_id')
        ]
        
        for field, key, name, id_key in config:
            items = d.get(field, [])
            if items:
                v_list = [{"n": "全部", "v": ""}]
                for i in items:
                    if id_key:
                        v_list.append({"n": i.get('name'), "v": str(i.get(id_key))})
                    else:
                        # 特殊处理年份这种直接是列表的情况
                        v_list.append({"n": str(i), "v": str(i)})
                filters.append({"key": key, "name": name, "value": v_list})
        
        # 添加通用排序
        filters.append({
            "key": "sort", 
            "name": "排序", 
            "value": [
                {"n": "最新", "v": "latest"},
                {"n": "最热", "v": "hot"},
                {"n": "评分", "v": "score"}
            ]
        })
        return filters

    def clean_vod_list(self, data_list):
        """统一清洗视频列表数据"""
        videos = []
        for item in data_list:
            remarks = item.get('remarks')
            if not remarks: 
                remarks = str(item.get('published_year', ''))
            
            videos.append({
                'vod_id': str(item.get('video_id')),
                'vod_name': item.get('title'),
                'vod_pic': item.get('cover_image'),
                'vod_remarks': remarks,
                'vod_year': str(item.get('published_year', ''))
            })
        return videos

    def fetch_json(self, url):
        """封装通用请求"""
        try:
            import requests
            import urllib3
            urllib3.disable_warnings()
            
            # 超时设置短一点，提高并发效率
            resp = requests.get(url, headers=self.headers, timeout=5, verify=False)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def format_list(self, items):
        """格式化演员/导演列表"""
        if not items: return ""
        names = []
        for i in items:
            if isinstance(i, dict): names.append(i.get('name', ''))
            elif isinstance(i, str): names.append(i)
        return ','.join(names)
