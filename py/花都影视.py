# coding=utf-8
# !/usr/bin/python

"""

作者 丢丢喵 集多 乐哥 兔爷 内容均从互联网收集而来 仅供交流学习使用 严禁用于商业用途 请于24小时内删除
         ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import urllib3
import base64
import html
import json
import time
import sys
import re
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('..')

xurl = "https://www.net.hdys1.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': xurl,
    'sec-ch-ua': '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
         }

class Spider(Spider):
    
    def getName(self):
        return "丢丢喵"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeVideoContent(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""
        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")
        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg
        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def get_page_with_dynamic_cookie(self, target_url):
        local_headers = headers.copy()
        session = requests.Session()
        session.headers.update(local_headers)
        session.verify = False
        try:
            resp = session.get(target_url, timeout=10)
            if resp.status_code in [404, 503, 403]:
                if session.cookies:
                    resp = session.get(target_url, timeout=10)
                    if resp.status_code == 200:
                        return resp.text
                    else:
                        print(1)
                else:
                    print(2)
            elif resp.status_code == 200:
                return resp.text
            else:
                print(3)
        except Exception as e:
            return None

    def homeContent(self, filter):
        result = {"class": []}
        html_content = self.fetch_home_page()
        doc = self.parse_and_unescape(html_content)
        soups = self.find_nav_elements(doc)
        self.extract_and_append_classes(soups, result)
        return result

    def fetch_home_page(self):
        target_url = f'{xurl}/index.php'
        return self.get_page_with_dynamic_cookie(target_url)

    def parse_and_unescape(self, html_content):
        res = html.unescape(html_content)
        return BeautifulSoup(res, "lxml")

    def find_nav_elements(self, doc):
        return doc.find_all('ul', class_="hidden-sm")

    def extract_and_append_classes(self, soups, result):
        for soup in soups:
            for vod in soup.find_all('a'):
                result["class"].append(self.parse_class_item(vod))

    def parse_class_item(self, vod):
        name = vod.text.strip()
        id = vod['href']
        return {"type_id": id, "type_name": name}

    def categoryContent(self, cid, pg, filter, ext):
        page = self.get_page_number(pg)
        target_url = self.build_category_url(cid, page)
        html_content = self.get_page_with_dynamic_cookie(target_url)
        doc = self.parse_and_unescape(html_content)
        soups = self.find_vod_lists(doc)
        videos = self.extract_videos(soups)
        return self.build_category_result(videos, pg)

    def get_page_number(self, pg):
        return int(pg) if pg else 1

    def build_category_url(self, cid, page):
        fenge = cid.split("---.html")
        return f'{xurl}{fenge[0]}{str(page)}---.html'

    def parse_and_unescape(self, html_content):
        res = html.unescape(html_content)
        return BeautifulSoup(res, "lxml")

    def find_vod_lists(self, doc):
        return doc.find_all('ul', class_="stui-vodlist")

    def extract_videos(self, soups):
        videos = []
        for soup in soups:
            for vod in soup.find_all('li'):
                videos.append(self.parse_video_item(vod))
        return videos

    def parse_video_item(self, vod):
        names = vod.find('a', class_="stui-vodlist__thumb")
        name = names['title']
        id = names['href']
        pic = vod.find('img')['data-original']
        remarks = vod.find('span', class_="pic-tag-b")
        remark = remarks.text.strip() if remarks else ""
        years = vod.find('span', class_="text-overflow")
        year = years.text.strip() if years else ""
        return {"vod_id": id,"vod_name": name,"vod_pic": pic,"vod_year": year,"vod_remarks": remark}

    def build_category_result(self, videos, pg):
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = self.prepare_did(ids[0])
        html_content = self.get_page_with_dynamic_cookie(did)
        res = self.unescape_html(html_content)
        doc = self.parse_html(res)
        content = self.build_content(res)
        actor = self.extract_actor(res)
        remarks = self.extract_remarks(res)
        year = self.extract_year(res)
        bofang = self.extract_play_url(res)
        videos = [self.build_video_data(did, actor, remarks, year, content, bofang)]
        return self.build_result(videos)

    def prepare_did(self, did):
        return xurl + did if 'http' not in did else did

    def unescape_html(self, html_content):
        return html.unescape(html_content)

    def parse_html(self, html):
        return BeautifulSoup(html, "lxml")

    def build_content(self, res):
        return '😸丢丢为您介绍剧情📢' + self.extract_middle_text(res, '名称：', '</li>', 1, 'alt=".*?">(.*?)</span>')

    def extract_actor(self, res):
        return self.extract_middle_text(res, '演员：', '<a', 1, 'alt="(.*?)">')

    def extract_remarks(self, res):
        return self.extract_middle_text(res, '类别：', '</li>', 1, 'target=".*?">(.*?)</a>')

    def extract_year(self, res):
        return self.extract_middle_text(res, '日期：</strong>', '<', 0)

    def extract_play_url(self, res):
        return self.extract_middle_text(res, 'class="btn btn-primary" href="', '"', 0)

    def build_video_data(self, did, actor, remarks, year, content, bofang):
        return {"vod_id": did,"vod_actor": actor,"vod_remarks": remarks,"vod_year": year,"vod_content": content,"vod_play_from": "花都专线","vod_play_url": bofang}

    def build_result(self, videos):
        result = {}
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        id = self.prepare_id(id)
        html_content = self.get_page_with_dynamic_cookie(id)
        res = self.unescape_html(html_content)
        url = self.extract_and_decode_url(res)
        return self.build_player_result(url)

    def prepare_id(self, id):
        return xurl + id if 'http' not in id else id

    def unescape_html(self, html_content):
        return html.unescape(html_content)

    def extract_and_decode_url(self, res):
        url = self.extract_middle_text(res, '"","url":"', '"', 0).replace('\\', '')
        base64_decoded_bytes = base64.b64decode(url)
        base64_decoded_string = base64_decoded_bytes.decode('utf-8')
        return unquote(base64_decoded_string)

    def build_player_result(self, url):
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg):
        page = self.get_page_number(pg)
        did = self.build_search_url(key, page)
        html_content = self.get_page_with_dynamic_cookie(did)
        res = self.unescape_html(html_content)
        doc = self.parse_html(res)
        soups = self.find_vod_lists(doc)
        videos = self.extract_search_videos(soups)
        return self.build_search_result(videos, pg)

    def get_page_number(self, pg):
        return int(pg) if pg else 1

    def build_search_url(self, key, page):
        return f'{xurl}/vodsearch/{key}----------{str(page)}---.html'

    def unescape_html(self, html_content):
        return html.unescape(html_content)

    def parse_html(self, html):
        return BeautifulSoup(html, "lxml")

    def find_vod_lists(self, doc):
        return doc.find_all('ul', class_="stui-vodlist")

    def extract_search_videos(self, soups):
        videos = []
        for item in soups:
            for vod in item.find_all('li'):
                videos.append(self.parse_search_video_item(vod))
        return videos

    def parse_search_video_item(self, vod):
        names = vod.find('a', class_="stui-vodlist__thumb")
        name = names['title']
        id = names['href']
        pic = vod.find('img')['data-original']
        remarks = vod.find('span', class_="pic-tag-b")
        remark = remarks.text.strip() if remarks else ""
        years = vod.find('span', class_="text-overflow")
        year = years.text.strip() if years else ""
        return {"vod_id": id,"vod_name": name,"vod_pic": pic,"vod_year": year,"vod_remarks": remark}

    def build_search_result(self, videos, pg):
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None












