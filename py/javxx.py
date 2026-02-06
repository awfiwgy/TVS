# -*- coding: utf-8 -*-
import gzip,json,re,sys,base64,requests
from base64 import b64decode
from urllib.parse import unquote,urlparse
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    host,contr = 'https://javxx.com','cn'
    conh = f'{host}/{contr}'
    headers = {'accept-language':'zh-CN,zh;q=0.9,en;q=0.8','referer':f'{conh}/','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
    gcate = 'H4sIAAAAAAAAA6tWejan4dm0DUpWCkp5qeVKOkrPm9e+nL4CxM/ILwHygfIv9k8E8YtSk1PzwELTFzxf0AgSKs0DChXnF6WmwIWfbW55OWcTqqRuTmpiNljN8427n3asBsmmp+YVpRaDtO2Z8nTiDJBQYnIJUKgYLPq0Y9uTvXOeTm0DSeQCdReBRJ9vBmqfDhIqTi3KhGhf0P587T6QUElierFSLQCk4MAf0gAAAA=='
    flts = 'H4sIAAAAAAAAA23QwYrCMBAG4FeRnH0CX0WKBDJiMRpoY0WkIOtFXLQU1IoEFFHWw4qHPazgii/TRPctNKK1Ro/zz8cM/PkmKkMD5TLIZQ5HWVTFFUiNHqY1PeebyNOxAxSwCwWCOWitMxmEcttW0VKJKfKzN4kJAfLk1O9OdmemKzF+B8f2+j9aPVacEdwoeDbU3TuJd93LgdPXx1F8PmAdoEwNqTaBDFemrLAqL72hSnReqcuvDkgCRUsGkfqenw59AxaxxxybP9uRuFjkW5reai7alIOTKjoJzKoxpUnDvWG8bcnlj/obyHCcKi95JxeTeN9LEcu3zoYr9GndAQAA'
    actft = 'H4sIAAAAAAAAA22UTUsbURSG/0qYtQMxZvIhIvidxI/oVpEy6GiCmpFkEhEpVBcqikYprV2kG6GkhYK2XRbxzziT+C88c2/OnLnnunznec47zJ3LWTsydpxDYzRhVJzqdsUzhoyavecoD1r2bjN8snZktEIwPJI0h0fSoRqL/vW33p9/xsehyLLgcZ4sETUrDcNp6pJRt2A4TV0yapYFwxZ1yahbMGxRl4yalYHhDHXJqFswnKEuGTUrC8NZ6pJRt2A4S10yalYOhnPUJaNuwXCOumTUrDwM56lLRrTWQ29wNzaa+7GLIRO/FRPYM9F7+hV8f6D3TCKZ5GQKyRQn00imOZlBMsPJLJJZTuaQzHFSQFLgpIikyEkJSYmTeSTznCwgWeBkEckiJ0tIljgpIylzsoxkmZMVJCucrCJZRRL/9/a2E/v3MvF/H14cLBlLpJL+32OqTyXNVHTJRFCxZaaiYREUDMuFVo0IKrZM2jEiKBjWCS0XEVRsmbRVRFAwLBBaJyIoGHZCPpoeT2TkZ8fPruHW4xt1EPnpCTyo8buf/ZsreseG26x5CPvd09f72+DL4+tZmxTP3bQPP7SqzkEDxZf/F8Hdj373pNe5JPHAcXZ2mRk8tP3bn9zcc2te5R016JzrasMTnrMZiZ1Pfvsu+H3ff75m4pbdcutVT3W/dsAND279DSxD8pmOBgAA'

    def init(self, extend='{}'):
        c = json.loads(extend)
        self.proxies,self.plp = c.get('proxy',{}),c.get('plp','')
    def getName(self): pass
    def isVideoFormat(self, url): pass
    def manualVideoCheck(self): pass
    def destroy(self): pass

    def homeContent(self, filter):
        d = self.getpq(requests.get(self.conh,headers=self.headers,proxies=self.proxies).text)
        cate = self.ungzip(self.gcate)
        cls,flts = [],{}
        for k,j in cate.items():
            cls.append({'type_name':k,'type_id':j})
            flts[j] = self.ungzip(self.actft if j=='actresses' else self.flts)
        return {'class':cls,'filters':flts,'list':self.getvl(d('.vid-items .item'))}

    def homeVideoContent(self): pass

    def categoryContent(self, tid, pg, filter, extend):
        vds,pgc = [],1
        if tid in ['genres','makers','series','tags']:
            g = tid if tid=='series' else tid[:-1]
            d = self.getpq(requests.get(f"{self.conh}/{tid}",headers=self.headers,proxies=self.proxies).text)
            for i in d(f'.term-items.{g} .item').items():
                vds.append({'vod_id':i('a').attr('href'),'vod_name':i('h2').text(),'vod_remarks':i('.meta').text(),'vod_tag':'folder','style':{"type":"rect","ratio":2}})
        elif tid == 'actresses':
            p = {k:v for k,v in {"height":extend.get('height'),"cup":extend.get('cup'),"sort":extend.get('sort'),"age":extend.get('age'),"page":pg}.items() if v}
            d = self.getpq(requests.get(f"{self.conh}/{tid}",headers=self.headers,params=p,proxies=self.proxies).text)
            pgc = self.getpgc(d('ul.pagination li').eq(-1))
            for i in d('.chanel-items .item').items():
                m = i('.main')
                vds.append({'vod_id':m('.info a').attr('href'),'vod_name':m('.info h2').text(),'vod_pic':m('.avatar img').attr('src'),'vod_year':m('.meta div div').eq(-1).text(),'vod_remarks':m('.meta div div').eq(0).text(),'vod_tag':'folder','style':{"type":"oval","ratio":0.75}})
        else:
            tid = tid.split('_click')[0].replace(f"/{self.contr}/","")
            p = {k:v for k,v in {"filter":extend.get('filter'),"sort":extend.get('sort'),"page":pg}.items() if v}
            d = self.getpq(requests.get(f"{self.conh}/{tid}",params=p,headers=self.headers,proxies=self.proxies).text)
            vds,pgc = self.getvl(d('.vid-items .item')),self.getpgc(d('ul.pagination li').eq(-1))
        return {'list':vds,'page':pg,'pagecount':pgc,'limit':90,'total':999999}

    def detailContent(self, ids):
        d = self.getpq(requests.get(f"{self.host}{ids[0]}",headers=self.headers,proxies=self.proxies).text)
        dv = d('#video-details')
        ps = {
            '播放列表': f"{d('#video-info h1').text()}${d('#video-files div').attr('data-url')}",
            '猜你喜欢': '#'.join([f"{i('.info .title span').eq(-1).text()}$_gggb_{i('.info .title').attr('href')}" for i in d('.main .vid-items .item').items()]),
            '相关推荐': '#'.join([f"{i('.info .title span').eq(-1).text()}$_gggb_{i('.info .title').attr('href')}" for i in d('.vid-items.side .item').items()])
        }
        n,p = [],[]
        for k,v in ps.items():
            if v: n.append(k); p.append(v)
        vod = {'vod_name':d('#video-info h1').text(),'vod_pic':d('.video-poster img').attr('src') or d('.poster img').attr('src'),'vod_content':dv('.content').text(),'vod_play_from':'$$$'.join(n),'vod_play_url':'$$$'.join(p)}
        a,b,c,e = [],[],[],[]
        for i in dv('.meta div').items():
            l,t = i('label').text(),i('span').text()
            if '发布' in l: vod['vod_year']=t
            elif '演员' in l: a.extend(['[a=cr:'+json.dumps({'id':f"{j.attr('href')}_click",'name':j.text()})+'/]'+j.text()+'[/a]' for j in i('a').items()])
            elif re.search('制作|系列',l): b.extend(['[a=cr:'+json.dumps({'id':f"{j.attr('href')}_click",'name':j.text()})+'/]'+j.text()+'[/a]' for j in i('a').items()])
            elif '标签' in l: c.extend(['[a=cr:'+json.dumps({'id':f"{j.attr('href')}_click",'name':j.text()})+'/]'+j.text()+'[/a]' for j in i('a').items()])
            elif '类别' in l: e.extend(['[a=cr:'+json.dumps({'id':f"{j.attr('href')}_click",'name':j.text()})+'/]'+j.text()+'[/a]' for j in i('a').items()])
        vod.update({'vod_actor':' '.join(a),'vod_director':' '.join(b),'vod_remarks':' '.join(c),'vod_content':' '.join(e)+'\n'+vod.get('vod_content','')})
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        d = self.getpq(requests.get(f"{self.conh}/search",headers=self.headers,params={'keyword':key,'page':pg},proxies=self.proxies).text)
        return {'list':self.getvl(d('.vid-items .item')),'page':pg}

    def playerContent(self, flag, id, vipFlags):
        if id.startswith('_gggb_'):
            d = self.getpq(requests.get(f"{self.host}{id.replace('_gggb_','')}",headers=self.headers).text)
            id = d('#video-files div').attr('data-url')
        u = self.de_url(id)
        vid = urlparse(u).path.split('/')[-1]
        res = requests.get(f"https://surrit.store/stream?src=javxx&poster=&token={self.ev(vid)}",timeout=10).json()
        return {'parse':0,'url':json.loads(self.dm(res["result"]["media"]))["stream"],'header':{'user-agent':self.headers['user-agent'],'origin':'https://surrit.store','referer':'https://surrit.store/'}}

    def ev(self, v, k="ym1eS4t0jTLakZYQ"):
        kb = k.encode()
        return base64.b64encode(bytes([ord(v[i])^kb[i%len(kb)] for i in range(len(v))])).decode()

    def dm(self, m, k="ym1eS4t0jTLakZYQ"):
        eb,kb = base64.b64decode(m),k.encode()
        return unquote(''.join([chr(eb[i]^kb[i%len(kb)]) for i in range(len(eb))]))

    def getvl(self, data):
        vids = []
        for i in data.items():
            img = i('.img')
            vids.append({'vod_id':img('a').attr('href'),'vod_name':i('.info .title').text(),'vod_pic':img('.image img').attr('src'),'vod_year':i('.info .meta div').eq(-1).text(),'vod_remarks':i('.duration').text(),'style':{"type":"rect","ratio":1.33}})
        return vids

    def de_url(self, s, k="G9zhUyphqPWZGWzZ"):
        d = b64decode(s).decode()
        return unquote(''.join([chr(ord(d[i])^ord(k[i%len(k)])) for i in range(len(d))]))

    def getpgc(self, d):
        try: return int(d('a').attr('href').split('page=')[-1]) if d and d('a') else int(d.text()) if d else 1
        except: return 1

    def ungzip(self, d): return json.loads(gzip.decompress(b64decode(d)).decode())
    def getpq(self, d):
        try: return pq(d)
        except: return pq(d.encode('utf-8'))
