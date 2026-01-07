# -*- coding: utf-8 -*-
import re
import urllib.parse
import requests
from base64 import b64encode

# 尝试导入 Crypto 库，防止环境缺失报错
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
#发布页https://wanwuu.com/contact
class Spider:
    def __init__(self):
        self.name = '玩物社区'
        self.host = 'https://wanwuu.com'
        self.default_pic = 'https://via.placeholder.com/400x225?text=Video'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.host,
        }
        self.classes = []
        # 分类配置
        category_str = "国产SM$guochan-sm#日韩SM$rihan-sm#欧美SM$oumei-sm#直播回放$zhibo-huifang"
        for item in category_str.split('#'):
            if '$' in item:
                name, path = item.split('$')
                self.classes.append({"type_name": name, "type_id": path})

    # --- AES 解密图片逻辑 ---
    def _decrypt_pic(self, img_url):
        if not HAS_CRYPTO:
            return img_url 
        try:
            img_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7390.55 Safari/537.36',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="141", "Google Chrome";v="141"',
                'Origin': 'https://xgne8.dyxobic.cc',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            response = requests.get(img_url, headers=img_headers, timeout=5)
            if response.status_code != 200:
                return self.default_pic
            key = b"f5d965df75336270"
            iv = b'97b60394abc2fbe1'
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(response.content), AES.block_size)
            b64_code = b64encode(pt).decode()
            return f"data:image/jpeg;base64,{b64_code}"
        except Exception as e:
            return self.default_pic

    def getDependence(self): return []
    def getName(self): return self.name
    def isVideoFormat(self, url): return False
    def manualVideoCheck(self): pass
    def init(self, extend=""): pass

    def homeContent(self, filter):
        return {"class": self.classes}

    def homeVideoContent(self):
        return self.categoryContent("guochan-sm", "1", False, {})

    def _parse_videos(self, html):
        """解析视频列表通用逻辑"""
        videos = []
        # 针对首页.HTML结构优化正则
        pattern = r'<div class="video-item"[^>]*>(.*?)</div>\s*</li>'
        if not re.search(pattern, html, re.S):
             pattern = r'<div class="video-item"[^>]*>(.*?)</div>'

        for block in re.findall(pattern, html, re.S):
            # 1. 链接
            href_match = re.search(r'href="([^"]+)"', block)
            if not href_match: continue
            href = href_match.group(1)
            
            # 2. 标题
            title = ""
            title_match = re.search(r'<a[^>]+class="[^"]*line-clamp-2[^"]*"[^>]*>([^<]+)</a>', block)
            if title_match:
                title = title_match.group(1).strip()
            else:
                alt_match = re.search(r'alt="([^"]+)"', block)
                if alt_match: title = alt_match.group(1).strip()
            if not title: continue

            # 3. 图片 (优先 data-src)
            pic = ""
            pic_match = re.search(r'data-src="([^"]+)"', block)
            if pic_match:
                pic = pic_match.group(1)
            else:
                src_match = re.search(r'src="([^"]+)"', block)
                if src_match and "poster_loading" not in src_match.group(1):
                    pic = src_match.group(1)

            # 图片解密处理
            pic = self._abs(pic)
            if 'rulbbz.cn' in pic:
                pic = self._decrypt_pic(pic)

            # 4. 时长
            remark = ""
            dur_match = re.search(r'opacity-50[^>]*>\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*<', block)
            if dur_match:
                remark = dur_match.group(1)

            videos.append({
                "vod_id": href,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        return videos

    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg)
            if tid in ["novels/new", "posts/all"]:
                url = f"{self.host}/{tid}/page/{pg}/" if pg > 1 else f"{self.host}/{tid}/"
            else:
                prefix = "/videos/" if not tid.startswith("videos/") else "/"
                url = f"{self.host}{prefix}{tid}/page/{pg}/" if pg > 1 else f"{self.host}{prefix}{tid}/"
            
            # URL 规范化
            url = url.replace('//videos', '/videos').replace('https:/w', 'https://w')
            
            r = requests.get(url, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            return self._page(self._parse_videos(r.text), pg)
        except Exception as e:
            return self._page([], pg)

    def searchContent(self, key, quick, pg='1'):
        try:
            pg = int(pg)
            wd = urllib.parse.quote(key)
            url = f"{self.host}/videos/search/{wd}/page/{pg}/" if pg > 1 else f"{self.host}/videos/search/{wd}/"
            r = requests.get(url, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            return self._page(self._parse_videos(r.text), pg)
        except Exception as e:
            return self._page([], pg)

    def detailContent(self, array):
        vid = array[0]
        if not vid.startswith('http'):
            vid = self._abs(vid)
            
        try:
            r = requests.get(vid, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            html = r.text

            # 提取标题
            title = ""
            h1_match = re.search(r'<h1[^>]*dx-title[^>]*>(.*?)</h1>', html)
            if h1_match:
                title = h1_match.group(1).strip()
            else:
                title_match = re.search(r'<meta property="og:title" content="(.*?)"', html)
                if title_match: title = title_match.group(1).strip()

            # 提取图片
            pic = ""
            pic_match = re.search(r'<meta property="og:image" content="(.*?)"', html)
            if pic_match:
                pic = self._abs(pic_match.group(1))
                if 'rulbbz.cn' in pic: pic = self._decrypt_pic(pic)

            # 提取简介
            desc = ""
            desc_match = re.search(r'<meta property="og:description" content="(.*?)"', html)
            if desc_match: desc = desc_match.group(1).strip()

            # --- 关键修复：提取 Embed URL 或 Video ID ---
            # 优先从 twitter:player meta 标签提取，这是最干净的播放地址
            play_url = ""
            embed_match = re.search(r'<meta name="twitter:player" content="(.*?)"', html)
            if embed_match:
                play_url = embed_match.group(1)
            else:
                # 备用方案：提取ID拼接URL
                id_match = re.search(r'data-video_id="(\d+)"', html)
                if not id_match:
                    id_match = re.search(r'const _detail_ = \{.*?"id":(\d+),', html, re.S)
                
                if id_match:
                    video_id = id_match.group(1)
                    play_url = f"{self.host}/videos/embed?id={video_id}"
                else:
                    # 最后的保底：直接使用页面URL（可能会嗅探到广告）
                    play_url = vid

            vod = {
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "type_name": "SM",
                "vod_content": desc,
                "vod_play_from": "玩物社区",
                "vod_play_url": f"点击播放${play_url}"  # 将 Embed URL 传递给 playerContent
            }
            return {"list": [vod]}
        except Exception as e:
            return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        """
        id: 现在接收的是 /videos/embed?id=... 这样的干净嵌入页URL
        """
        return {
            "parse": 1,         # 开启嗅探，因为 m3u8 是通过 JS 动态生成的
            "playUrl": "",
            "url": id, 
            "header": {
                "User-Agent": self.headers['User-Agent'],
                "Referer": self.host  # 必须带 Referer，否则嵌入页可能拒绝访问
            }
        }

    def _abs(self, url):
        if not url: return ""
        if url.startswith("data:image"): return url
        if url.startswith('http'): return url
        if url.startswith('//'): return 'https:' + url
        return urllib.parse.urljoin(self.host, url)

    def _page(self, videos, pg):
        return {
            "list": videos, 
            "page": int(pg), 
            "pagecount": 9999, 
            "limit": 24, 
            "total": 999999
        }
    
    def localProxy(self, param):
        return []
