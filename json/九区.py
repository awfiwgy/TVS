import sys
import json
import time
import urllib.parse
import re
import requests
from lxml import etree
from urllib.parse import urljoin
import hashlib
import base64

class NewSpider:
    
    def __init__(self):
        self.name = "苹果视频(新站)"
        self.host = "https://618041.xyz"  # 根据实际域名调整
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        self.special_categories = ['40', '39', '37', '36', '38', '41', '28', '29', '33', '30', '27', '26']
        print(f"[{self.name}] 爬虫初始化完成")
    
    def getName(self):
        return self.name
    
    def init(self, extend=""):
        # 初始化设置
        pass
    
    def homeContent(self, filter):
        """获取首页内容和分类"""
        result = {}
        classes = [
            {'type_id': '1', 'type_name': '全部视频'},
            {'type_id': '40', 'type_name': '无码专区'},
            {'type_id': '39', 'type_name': '中文字幕'},
            {'type_id': '37', 'type_name': '网红主播'},
            {'type_id': '36', 'type_name': '传媒制作'},
            {'type_id': '38', 'type_name': '国产视频'},
            {'type_id': '41', 'type_name': '热门推荐'},
            {'type_id': '28', 'type_name': '成人动漫'},
            {'type_id': '29', 'type_name': 'OnlyFans'},
            {'type_id': '33', 'type_name': '无码专区2'},
            {'type_id': '30', 'type_name': 'FC2视频'},
            {'type_id': '27', 'type_name': '字幕专区'},
            {'type_id': '26', 'type_name': '国产自拍'}
        ]
        result['class'] = classes
        
        try:
            rsp = requests.get(self.host, headers=self.headers, timeout=10, verify=False)
            doc = etree.HTML(rsp.text)
            videos = self._get_videos(doc, limit=20)
            result['list'] = videos
        except Exception as e:
            print(f"[{self.name}] 首页获取出错: {str(e)}")
            result['list'] = []
        return result
    
    def categoryContent(self, tid, pg, filter, extend):
        """获取分类内容"""
        try:
            url = f"{self.host}/index.php/vod/type/id/{tid}.html"
            if pg and pg != '1':
                url = url.replace('.html', f'/page/{pg}.html')
            
            print(f"[{self.name}] 访问分类URL: {url}")
            rsp = requests.get(url, headers=self.headers, timeout=10, verify=False)
            doc = etree.HTML(rsp.text)
            
            videos = self._get_videos(doc, category_id=tid)
            
            # 尝试获取总页数
            pagecount = 242  # 从HTML中获取的默认值
            try:
                # 从script标签中提取totalPages
                script_content = rsp.text
                match = re.search(r"const totalPages='(\d+)'", script_content)
                if match:
                    pagecount = int(match.group(1))
            except:
                pass
            
            total = pagecount * 20  # 估算总数
            
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': 20,
                'total': total
            }
        except Exception as e:
            print(f"[{self.name}] 分类内容获取出错: {str(e)}")
            return {'list': []}
    
    def searchContent(self, key, quick, pg="1"):
        """搜索功能"""
        try:
            search_url = f"{self.host}/index.php/vod/type/id/1/wd/{urllib.parse.quote(key)}/page/{pg}.html"
            print(f"[{self.name}] 搜索URL: {search_url}")
            
            rsp = requests.get(search_url, headers=self.headers, timeout=10, verify=False)
            doc = etree.HTML(rsp.text)
            videos = self._get_videos(doc)
            
            # 尝试获取总页数
            pagecount = 5
            total = pagecount * 20
            
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': 20,
                'total': total
            }
        except Exception as e:
            print(f"[{self.name}] 搜索出错: {str(e)}")
            return {'list': []}
    
    def detailContent(self, ids):
        """获取详情"""
        try:
            vid = ids[0]
            
            # 检查是否是特殊链接
            if vid.startswith('scsc_'):
                # 解析格式: scsc_{category_id}_{video_hash}_{encoded_url}
                parts = vid.split('_')
                if len(parts) >= 4:
                    category_id = parts[1]
                    video_hash = parts[2]
                    encoded_url = '_'.join(parts[3:])
                    play_url = urllib.parse.unquote(encoded_url)
                    
                    # 从URL中提取视频ID
                    video_id = self._extract_video_id_from_url(play_url)
                    
                    # 从链接中提取加密标题
                    parsed_url = urllib.parse.urlparse(play_url)
                    path = parsed_url.path
                    if '/html/scsc/' in path:
                        title_part = path.split('/html/scsc/')[1].replace('.html', '')
                        title = self._decrypt_title(title_part)
                    else:
                        title = "未知标题"
                    
                    # 获取封面图
                    cover_url = f"https://assets.tbsp7.xyz/thumbnail/video/videoID/{video_id}/ratio_4_3"
                    
                    return {
                        'list': [{
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': cover_url,
                            'vod_remarks': '',
                            'vod_year': '',
                            'vod_area': '',
                            'vod_actor': '',
                            'vod_director': '',
                            'vod_content': '',
                            'vod_play_from': '直接播放',
                            'vod_play_url': f"第1集${play_url}"
                        }]
                    }
            
            # 常规处理
            detail_url = f"{self.host}/index.php/vod/detail/id/{vid}.html"
            print(f"[{self.name}] 访问详情URL: {detail_url}")
            
            rsp = requests.get(detail_url, headers=self.headers, timeout=10, verify=False)
            doc = etree.HTML(rsp.text)
            
            # 提取详情信息
            title = self._get_text(doc, ['//h1/text()', '//title/text()'])
            pic = self._get_text(doc, ['//div[contains(@class,"dyimg")]//img/@src', '//img[@class="lazy"]/@data-cover'])
            
            if pic and pic.startswith('/'):
                pic = self.host + pic
            
            desc = self._get_text(doc, ['//div[contains(@class,"yp_context")]/text()', '//div[contains(@class,"introduction")]//text()'])
            actor = self._get_text(doc, ['//span[contains(text(),"主演")]/following-sibling::*/text()'])
            director = self._get_text(doc, ['//span[contains(text(),"导演")]/following-sibling::*/text()'])
            
            # 查找播放链接
            play_links = doc.xpath('//a[contains(@href, "/html/scsc/")]/@href')
            if not play_links:
                play_links = doc.xpath('//a[contains(@href, "id=")]/@href')
            
            play_from = []
            play_urls = []
            
            if play_links:
                episodes = []
                for link in play_links:
                    if link.startswith('/'):
                        full_url = urljoin(self.host, link)
                    else:
                        full_url = link
                    episodes.append(f"第1集${full_url}")
                
                if episodes:
                    play_from.append("默认播放源")
                    play_urls.append('#'.join(episodes))
            
            if not play_from:
                play_from.append("默认播放源")
                play_urls.append(f"第1集${vid}")
            
            return {
                'list': [{
                    'vod_id': vid,
                    'vod_name': title,
                    'vod_pic': pic,
                    'type_name': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_remarks': '',
                    'vod_actor': actor,
                    'vod_director': director,
                    'vod_content': desc,
                    'vod_play_from': '$$$'.join(play_from),
                    'vod_play_url': '$$$'.join(play_urls)
                }]
            }
            
        except Exception as e:
            print(f"[{self.name}] 详情获取出错: {str(e)}")
            return {'list': []}
    
    def playerContent(self, flag, id, vipFlags):
        """获取播放链接"""
        try:
            print(f"[{self.name}] 获取播放链接: flag={flag}, id={id}")
            
            # 检查是否是特殊链接
            if id.startswith('scsc_'):
                parts = id.split('_')
                if len(parts) >= 4:
                    encoded_url = '_'.join(parts[3:])
                    play_url = urllib.parse.unquote(encoded_url)
                    
                    # 直接提取视频地址
                    parsed_url = urllib.parse.urlparse(play_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    video_url = query_params.get('id', [''])[0]
                    if not video_url:
                        # 尝试从路径中提取
                        if 'id=' in play_url:
                            video_url = play_url.split('id=')[1]
                    
                    if video_url:
                        # 确保URL是完整的
                        if video_url.startswith('//'):
                            video_url = 'https:' + video_url
                        elif not video_url.startswith('http'):
                            video_url = urljoin('https://assets.tbsp7.xyz', video_url)
                        
                        print(f"[{self.name}] 提取到视频地址: {video_url}")
                        return {'parse': 0, 'playUrl': '', 'url': video_url}
                    else:
                        return {'parse': 1, 'playUrl': '', 'url': play_url}
            
            # 如果是完整URL
            if id.startswith('http'):
                parsed_url = urllib.parse.urlparse(id)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                video_url = query_params.get('id', [''])[0]
                if not video_url:
                    video_url = query_params.get('v', [''])[0]
                
                if video_url:
                    # 确保URL是完整的
                    if video_url.startswith('//'):
                        video_url = 'https:' + video_url
                    elif not video_url.startswith('http'):
                        video_url = urljoin('https://assets.tbsp7.xyz', video_url)
                    
                    print(f"[{self.name}] 从URL中提取到视频地址: {video_url}")
                    return {'parse': 0, 'playUrl': '', 'url': video_url}
                else:
                    return {'parse': 1, 'playUrl': '', 'url': id}
            
            # 其他情况，返回原始ID
            return {'parse': 1, 'playUrl': '', 'url': id}
            
        except Exception as e:
            print(f"[{self.name}] 播放链接获取出错: {str(e)}")
            return {'parse': 1, 'playUrl': '', 'url': id}
    
    def _get_videos(self, doc, category_id=None, limit=20):
        """提取视频列表"""
        try:
            videos = []
            elements = doc.xpath('//a[@class="vodbox"]')
            print(f"[{self.name}] 找到 {len(elements)} 个视频元素")
            
            for elem in elements:
                video = self._extract_video(elem, category_id)
                if video:
                    videos.append(video)
            
            return videos[:limit] if limit else videos
        except Exception as e:
            print(f"[{self.name}] 提取视频列表出错: {str(e)}")
            return []
    
    def _extract_video(self, element, category_id=None):
        """提取单个视频信息"""
        try:
            # 获取链接
            link = element.xpath('./@href')[0]
            if link.startswith('/'):
                link = self.host + link
            
            # 检查是否是scsc链接
            is_scsc_link = '/html/scsc/' in link
            
            if is_scsc_link:
                # 提取视频ID
                parsed_url = urllib.parse.urlparse(link)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                video_url = query_params.get('id', [''])[0]
                if not video_url:
                    return None
                
                # 从视频URL中提取视频ID
                video_id = self._extract_video_id_from_url(video_url)
                
                # 生成唯一的视频ID
                video_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
                encoded_link = urllib.parse.quote(link)
                final_vod_id = f"scsc_{category_id}_{video_hash}_{encoded_link}"
                
                # 提取加密标题
                title_elem = element.xpath('.//p[@class="km-script"]/text()')
                if not title_elem:
                    title_elem = element.xpath('.//p/text()')
                
                if title_elem:
                    encrypted_title = title_elem[0].strip()
                    title = self._decrypt_title(encrypted_title)
                else:
                    # 从链接路径中提取标题
                    path = parsed_url.path
                    if '/html/scsc/' in path:
                        title_part = path.split('/html/scsc/')[1].replace('.html', '')
                        title = self._decrypt_title(title_part)
                    else:
                        title = "未知标题"
                
                # 提取封面图
                cover_elem = element.xpath('.//img/@data-cover')
                if cover_elem:
                    cover = cover_elem[0]
                else:
                    # 如果没有data-cover，使用默认封面URL
                    cover = f"https://assets.tbsp7.xyz/thumbnail/video/videoID/{video_id}/ratio_4_3"
                
                return {
                    'vod_id': final_vod_id,
                    'vod_name': title,
                    'vod_pic': cover,
                    'vod_remarks': '',
                    'vod_year': ''
                }
            else:
                # 常规链接处理
                vod_id_match = re.search(r'/id/(\d+)\.html', link)
                if vod_id_match:
                    vod_id = vod_id_match.group(1)
                else:
                    vod_id = str(hash(link) % 1000000)
                
                final_vod_id = vod_id
                if category_id:
                    final_vod_id = f"{category_id}_{vod_id}"
                
                # 提取标题
                title_elem = element.xpath('.//p[@class="km-script"]/text()')
                if not title_elem:
                    title_elem = element.xpath('.//p/text()')
                
                if title_elem:
                    encrypted_title = title_elem[0].strip()
                    title = self._decrypt_title(encrypted_title)
                else:
                    title = "未知标题"
                
                # 提取封面图
                cover_elem = element.xpath('.//img/@data-cover')
                if not cover_elem:
                    cover_elem = element.xpath('.//img/@src')
                
                cover = cover_elem[0] if cover_elem else ''
                if cover and cover.startswith('/'):
                    cover = self.host + cover
                
                return {
                    'vod_id': final_vod_id,
                    'vod_name': title,
                    'vod_pic': cover,
                    'vod_remarks': '',
                    'vod_year': ''
                }
                
        except Exception as e:
            print(f"[{self.name}] 提取视频信息出错: {str(e)}")
            return None
    
    def _decrypt_title(self, encrypted_text):
        """解密标题 (XOR 128)"""
        try:
            decrypted_chars = []
            for char in encrypted_text:
                code_point = ord(char)
                decrypted_code = code_point ^ 128
                decrypted_char = chr(decrypted_code)
                decrypted_chars.append(decrypted_char)
            
            decrypted_text = ''.join(decrypted_chars)
            # 清理特殊字符
            decrypted_text = decrypted_text.replace('&nbsp;', ' ')
            decrypted_text = decrypted_text.replace('Ý', ' ')
            decrypted_text = decrypted_text.replace('Û', ' ')
            return decrypted_text.strip()
        except Exception as e:
            print(f"[{self.name}] 标题解密失败: {str(e)}")
            return encrypted_text
    
    def _extract_video_id_from_url(self, video_url):
        """从视频URL中提取视频ID"""
        try:
            # 尝试匹配acg04536这样的格式
            match = re.search(r'acg(\d+)', video_url)
            if match:
                return match.group(0)
            
            # 尝试匹配数字ID
            match = re.search(r'videoID/(\d+)', video_url)
            if match:
                return match.group(1)
            
            # 使用哈希值
            return hashlib.md5(video_url.encode()).hexdigest()[:8]
        except:
            return "unknown"
    
    def _get_text(self, doc, selectors):
        """通用文本提取"""
        for selector in selectors:
            try:
                texts = doc.xpath(selector)
                for text in texts:
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return ''
    
    # 兼容性方法
    def homeVideoContent(self):
        return self.homeContent(None)
    
    def isVideoFormat(self, url):
        return True
    
    def manualVideoCheck(self):
        return False

# 使用示例
if __name__ == '__main__':
    spider = NewSpider()
    
    # 测试首页
    print("获取首页内容...")
    home_result = spider.homeContent(None)
    print(f"分类数量: {len(home_result.get('class', []))}")
    print(f"视频数量: {len(home_result.get('list', []))}")
    
    # 测试分类
    print("\n获取分类内容...")
    category_result = spider.categoryContent('28', '1', None, None)
    print(f"分类视频数量: {len(category_result.get('list', []))}")
    
    # 测试搜索
    print("\n测试搜索...")
    search_result = spider.searchContent('动漫', False, '1')
    print(f"搜索结果数量: {len(search_result.get('list', []))}")
    
    if search_result['list']:
        # 测试详情
        print("\n测试详情...")
        detail_result = spider.detailContent([search_result['list'][0]['vod_id']])
        print(f"详情获取: {'成功' if detail_result['list'] else '失败'}")
        
        if detail_result['list']:
            # 测试播放
            print("\n测试播放...")
            play_result = spider.playerContent('', detail_result['list'][0]['vod_id'], None)
            print(f"播放结果: {play_result}")