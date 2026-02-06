# -*- coding: utf-8 -*-

import json
import re
import sys
from urllib.parse import quote
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend='{}'):
        self.host=self.getHost()
        pass

    def destroy(self):
        pass

    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    def getHost(self):
        url="http://www.hsck.net/"
        html=self.fetch(url,headers=self.headers)
        script=pq(html.content)("script").text()
        match = re.search(r'=[^=]*?"([^"]*)"', script)
        if match:
            ref = match.group(1)
            resp=self.fetch(f"{ref}{url}&p=/",headers=self.headers,allow_redirects=False)
            return resp.headers.get("Location")
        return "http://1964ck.cc"

    def buildVods(self, its):
        vods=[]
        for item in its.items():
            a=item("h4 > a")
            if "/vodplay/" not in a.attr("href"):continue
            vods.append({
                'vod_id': a.attr("href"),
                'vod_name': a.text(),
                'vod_pic': item("a").attr("data-original"),
                'vod_remark': item(".pic-text.text-right").text(),
            })
        return vods

    def homeContent(self, filter):
        resp=self.fetch(self.host,headers=self.headers)
        doc=pq(resp.content)
        c1=doc("ul.stui-header__menu.clearfix > li")
        c2=doc("ul.stui-pannel__menu.clearfix > li")
        classes,t = [],set()
        for j in (c1+c2).items():
            a=j("a")
            a.remove("span")
            href=a.attr("href")
            match=re.search(r'\d+', href)
            if not match or match.group() in t:continue
            t.add(match.group())
            classes.append({
                'type_name': a.text(),
                'type_id': match.group()
            })
        result = {'class': classes, 'list': self.buildVods(doc("ul.stui-vodlist.clearfix > li"))}
        return result

    def categoryContent(self, tid, pg, filter, extend):
        resp=self.fetch(f"{self.host}/vodtype/{tid}-{pg}.html",headers=self.headers)
        doc=pq(resp.content)
        result = {'list': self.buildVods(doc("ul.stui-vodlist.clearfix > li")), 'page': pg, 'pagecount': 9999,'limit': 90, 'total': 999999}
        return result

    def detailContent(self, ids):
        url=f"{self.host}{ids[0]}"
        resp=self.fetch(url,headers=self.headers)
        doc=pq(resp.content)
        data=doc(".stui-player__video.clearfix > script").eq(0).text()
        script=json.loads(data.split("aaa=",1)[-1])
        play=script.get("url") or url
        vod = {
            'vod_content': doc(".stui-player__foot").text(),
            'vod_play_from': 'Hsck',
            'vod_play_url': f'{doc(".stui-pannel__head.clearfix > h3").eq(1).text()}${play}'
        }
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        resp=self.fetch(f"{self.host}/vodsearch/{quote(key)}----------{pg}---.html",headers=self.headers)
        doc=pq(resp.content)
        return {'list': self.buildVods(doc("ul.stui-vodlist.clearfix > li"))}

    def playerContent(self, flag, id, vipFlags):
        return  {'parse': 0 if ".m3u" in id else 1, 'url': id}
