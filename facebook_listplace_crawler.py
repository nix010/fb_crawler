import json
from pprint import pprint
import requests
import re
from datetime import datetime
from facebook_user_crawler import FbBaseCrawler

class FbPageListCrawler(FbBaseCrawler):
    
    # Default crawl from the first 10 pages
    pages_crawl = 3
    
    def __init__(self,keyword,email,password):
    
        self.r = requests.Session()
        self._keyword = keyword
        self._user = email
        self._pass = password
        self._next_page_cursor = {}
        self._auth_token = None
        pass
    
    def crawl_now(self):
        print('Crawl the first %d pages... \n' %self.pages_crawl)
        if not self._login_fb():
            print('Can\'t login ! pls check user and password')
            return
        if self.get_auth_param():
            print('Can\'t get auth token, please try again')
            return
        
        all_data = []
        
        for i in range(self.pages_crawl):
            api_url = 'https://www.facebook.com/browse/async/places/?dpr=1'
            resp = self._post(api_url,data=self._search_keyword_payload(),headers={'content-type':'application/x-www-form-urlencoded'})
            
            json_data = json.loads(resp.text[9:])
            all_data += self.handle_json_data(json_data)
            if not self._next_page_cursor:
                print('Stop')
                break
        return all_data

    def get_auth_param(self):
    
        resp = self._get('https://www.facebook.com/search/str/%s/keywords_places/' % self._keyword)
        tree = self.parser(resp.text)
        tree.find_all(self.filter_token)
        return self._auth_token is None

    def filter_token(self,tag):
        if tag.name == 'script':
            token = re.findall('{"token":"(.*?)"}',str(tag.string))
            if token:
                self._auth_token = token[0]
                return True
        return False
    
    def handle_json_data(self,data):
        
        self._search_cursor_dict(data)
        parsed_data = []
        list_places = data.get('payload',{}).get('results',[])
        
        for place_id in list_places.keys():
            value = list_places[place_id]
            info = value['entityInfo']['aboutInfo']
            info_obj = {
                'id'            :place_id,
                'address'       :info['address'],
                'name'          :info['name'],
                'category'      :info['category'],
                'phone'         :info['phone'],
                'rating'        :info['rating'],
                'rating_count'  :info['rating_count'],
                'status'        :info['status'],
                'url'           :info['url'],
                'map'           :value['entityInfo']['mapInfo'],
                
            }
            parsed_data.append(info_obj)
        
        return parsed_data
        
        
        
    
    
    def _search_cursor_dict(self,json_data):
        
        cursor = json_data.get('payload',{}).get('pagingOptions',{}).get('cursor')
        self._next_page_cursor = cursor
        
    
    def _search_keyword_payload(self):
        
        return {
            'query'         : 'str/%s/keywords_places' % self._keyword,
            'original_query': 'str/%s/keywords_places' % self._keyword,
            '__user'        : self._fbuser_id,
            'fb_dtsg'       : self._auth_token,
            '__a'           : '1',
            '__be'          : '1',
            '__pc'          : 'PHASED:DEFAULT',
            'cursor'        : self._next_page_cursor
        }

keyword = input('What industry do you want to find ? : ')
keyword = keyword.strip()
crawler = FbPageListCrawler(
    keyword=keyword,
    email='xxx',
    password='yyy',
)
all_data = crawler.crawl_now()
print('Places count %d ' % len(all_data))
pprint(all_data)
print('Places count %d ' % len(all_data))
