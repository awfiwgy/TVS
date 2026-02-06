#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2026/1/3
# @file    : 采集去广模板.py
_J='type_name'
_I='url'
_H='vod_pic'
_G='jx'
_F='parse'
_E='vod_id'
_D='vod_year'
_C='vod_remarks'
_B='vod_name'
_A='list'
import base64,json,sys,requests,re
from urllib import parse
sys.path.append('..')
from base.spider import Spider as BaseSpider
class Spider(BaseSpider):
	def __init__(self):super().__init__();self.debug=False;self.name='采集去广模板';self.error_play_url='https://kjjsaas-sh.oss-cn-shanghai.aliyuncs.com/u/3401405881/20240818-936952-fc31b16575e80a7562cdb1f81a39c6b0.mp4';self.home_url='';self.headers={'User-Agent':'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'};self.a=[]
	def getName(self):return self.name
	def init(self,extend='{}'):
		encode='ZGVmIGRlbF9hZHModXJsKToNCiAgICBoZWFkZXJzID0gew0KICAgICAgICAiVXNlci1BZ2VudCI6ICJNb3ppbGxhLzUuMCAoTGludXg7IEFuZHJvaWQgMTA7IEspIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMzUuMC4wLjAgTW9iaWxlIFNhZmFyaS81MzcuMzYiDQogICAgfQ0KICAgIHRyeToNCiAgICAgICAgc2Vzc2lvbiA9IHJlcXVlc3RzLnNlc3Npb24oKQ0KICAgICAgICByb290X3VybDEgPSB1cmwucnNwbGl0KCcvJywgbWF4c3BsaXQ9MSlbMF0gKyAnLycNCiAgICAgICAgcmVzcG9uc2UgPSBzZXNzaW9uLmdldCh1cmwsIGhlYWRlcnM9aGVhZGVycykNCiAgICAgICAgIyBwcmludChyZXNwb25zZS50ZXh0LnNwbGl0bGluZXMoKVstMV0pDQogICAgICAgIHVybDIgPSByb290X3VybDEgKyByZXNwb25zZS50ZXh0LnNwbGl0bGluZXMoKVstMV0NCiAgICAgICAgIyBwcmludCh1cmwyKQ0KICAgICAgICByb290X3VybDIgPSB1cmwyLnJzcGxpdCgnLycsIG1heHNwbGl0PTEpWzBdICsgJy8nDQogICAgICAgIHJlc3BvbnNlMiA9IHNlc3Npb24uZ2V0KHVybDIsIGhlYWRlcnM9aGVhZGVycykNCiAgICAgICAgdGV4dCA9IHJlLnN1YihyJyNFWFQtWC1ESVNDT05USU5VSVRZXG4oKC4qP1xuKXsxLDEwfSkjRVhULVgtRElTQ09OVElOVUlUWVxuJywgJycsIHJlc3BvbnNlMi50ZXh0KQ0KICAgICAgICB0ZXh0ID0gcmUuc3ViKHInI0VYVC1YLURJU0NPTlRJTlVJVFlcbigoLio/XG4pezJ9KSNFWFQtWC1FTkRMSVNUXG4nLCAnI0VYVC1YLUVORExJU1QnLCB0ZXh0KQ0KICAgICAgICB0ZXh0ID0gcmUuc3ViKHInI0VYVC1YLURJU0NPTlRJTlVJVFlcbicsICcnLCB0ZXh0KQ0KICAgICAgICB0ZXh0ID0gcmUuc3ViKHInKC4qXC50cy4qKScsIHJvb3RfdXJsMiArICdcXDEnLCB0ZXh0KQ0KICAgICAgICByZXR1cm4gdGV4dA0KICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZToNCiAgICAgICAgcHJpbnQoZSkNCiAgICByZXR1cm4gTm9uZQ==';exec(base64.b64decode(encode).decode(),globals())
		try:self.extend=json.loads(extend);self.home_url=self.extend[_I];self.a=self.extend['a']
		except Exception as e:print(e);exit('')
	def homeContent(self,filter):
		B='type_id';A='class';return_data={A:[],'filters':{},_A:[],_F:0,_G:0}
		try:
			response=requests.get(self.home_url+'?ac=list',headers=self.headers);a=self.a
			for i in response.json()[A]:
				if i[B]in a:continue
				return_data[A].append({B:i[B],_J:i[_J]})
		except Exception as e:print(e)
		return return_data
	def homeVideoContent(self):
		return_data={_A:[],_F:0,_G:0}
		try:
			response=requests.get(self.home_url+'?ac=detail',headers=self.headers)
			for i in response.json()[_A]:return_data[_A].append({_E:i[_E],_B:i[_B],_H:i[_H],_C:i[_C],_D:i[_D]})
		except Exception as e:print(e)
		return return_data
	def categoryContent(self,cid,page,filter,ext):
		return_data={_A:[],_F:0,_G:0}
		try:
			response=requests.get(self.home_url+f"?t={cid}&pg={page}&ac=detail",headers=self.headers)
			for i in response.json()[_A]:return_data[_A].append({_E:i[_E],_B:i[_B],_H:i[_H],_C:i[_C],_D:i[_D]})
		except Exception as e:print(e)
		return return_data
	def detailContent(self,did):
		E='vod_play_url';D='vod_content';C='vod_director';B='vod_actor';A='vod_area';return_data={_A:[],_F:0,_G:0};ids=did[0]
		try:response=requests.get(self.home_url+f"?ids={ids}&ac=detail",headers=self.headers);i=response.json()[_A][0];return_data[_A].append({_J:i[_J],_E:ids,_B:i[_B],_C:i[_C],_D:i[_D],A:i[A],B:i[B],C:i[C],D:i[D],'vod_play_from':'去他妈的垃圾广告',E:i[E]})
		except Exception as e:print(e)
		return return_data
	def searchContent(self,wd,quick,page='1'):
		return_data={_A:[],_F:0,_G:0}
		try:
			response=requests.get(self.home_url+f"?wd={wd}&pg={page}&ac=detail",headers=self.headers)
			for i in response.json()[_A]:return_data[_A].append({_E:i[_E],_B:i[_B],_H:i[_H],_C:i[_C],_D:i[_D]})
		except Exception as e:print(e)
		return return_data
	def playerContent(self,flag,pid,vipFlags):return_data={_I:self.error_play_url,_F:0,_G:0,'header':self.headers};return_data[_I]='proxy://do=py&url='+parse.quote_plus(pid);return return_data
	def localProxy(self,params):
		m3u8_text=globals()['del_ads'](parse.unquote(params[_I]))
		if m3u8_text:return[200,'application/vnd.apple.mpegurl',m3u8_text]
if __name__=='__main__':0
