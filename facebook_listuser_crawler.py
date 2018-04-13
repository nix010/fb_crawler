import json
import re
from pprint import pprint
import requests
from datetime import datetime
from facebook_user_crawler import FbBaseCrawler

class FbUserListCrawler(FbBaseCrawler):
    
    # Default crawl from the first 10 pages
    pages_crawl = 10
    
    def __init__(self,keyword,email,password):
        self.r = requests.Session()
        self._keyword = keyword
        self._user = email
        self._pass = password
        self._next_page_params = {}

        pass
    
    def crawl_now(self):
        if not self._login_fb():
            return print('Can\'t login ! pls check user and password')
        user_list = {}
        for i in range(self.pages_crawl):

            api_url = 'https://www.facebook.com/ajax/pagelet/generic.php/BrowseScrollingSetPagelet'
            resp = self._get(api_url, params=self._search_keyword_payload(keyword=self._keyword))
            json_data = json.loads(resp.content[9:])

            self._next_page_params = self._search_cursor_dict(json_data.get('jsmods', {}).get('require'))

            if json_data.get('payload') is None or json_data.get('payload') == []:
                print ('response-data-error')
                return
            _user_list = self._extract_post_info(json_data)
            print(_user_list)

            print('Page %s completed' % (str(i + 1)))
            if not isinstance(self._next_page_params, dict):
                print('Stop of page %d' % (i+1))
                print('next-page-error')
                break
            user_list = {**user_list,**_user_list}

        self.user_list = user_list

        user_ids = list(user_list.keys())
        return self.crawl_fb_info(user_ids)
    
    def crawl_fb_info(self,ids):
        parsed_data = []
        for user_fbid in ids:
            resp = self._get('https://www.facebook.com/{profile_id}/about?lst={fb_id}%3A{profile_id}%3A{timestamp}&section=overview'.format(**{
                'profile_id':user_fbid,
                'fb_id':self._fbuser_id,
                'timestamp':int(datetime.now().timestamp()),
            }))
            if not resp.content or resp.status_code != 200:
                print('Id info not available %s' % user_fbid)
                continue
            html = resp.content
            if not html:
                print('Id error %s' % user_fbid)
                continue
            tree = self.parser(html)
            locator = tree.find(lambda x: x.name=='script' and x.text[64:72]=="is_last:")
            id_attr = re.findall("{container_id:\"(.*?)\"}},", locator.text)
            if len(id_attr) == 0:
                continue
            id_attr = id_attr[0]
            html = tree.select_one('#%s'%id_attr)
            if not html:
                continue
            _html = str(html).replace(' --></code>','')
            html = _html.replace('<code id="%s"><!-- '%id_attr,'')
            tree = self.parser(html)
            data = self._extract_contract_data_from_html(tree)
            data['name'] = self.user_list.get(user_fbid,'')
            parsed_data.append(data)
        return parsed_data
    
    def _extract_contract_data_from_html(self,tree):
        email = tree.select_one("span._50f9._50f7") or tree.select_one("span._c24._2ieq a[href^='mailto']")
        address = tree.select_one("span.fsm")
        phone = tree.select_one('span[dir="ltr"]')
        website = tree.select_one('a[rel="me noopener nofollow"]')
        job = tree.select_one('div._c24._50f4')
        return {
            'email'     :email.text if email else '',
            'address'   :address.text.strip() if address else '',
            'phone'     :phone.text if phone else '',
            'website'   :website.text if website else '',
            'job'       :job.text.lstrip() if job else '',
        }
    
    def _extract_post_info(self,json_data):
        post_dict = {}
        attr_list = json_data.get('jsmods',{}).get('require')
        
        for _list in attr_list:
            if _list[0] == 'UFIController':
                _root = _list[3]
                _id = _root[2].get('feedbacktarget', {}).get('ownerid')
                
                post_dict[_id] = _root[1].get('ownerName')
        
        return post_dict
    
    def _search_cursor_dict(self,dict_list):
        
        if dict_list is None: return None
        for arr in dict_list:
            if len(arr) >= 4 and arr[1] == 'pageletComplete':
                return arr[3][0]
        return None
    
    def _search_keyword_payload(self,keyword):
        sub_query = {
            "bqf": "keywords_blended_posts(%s)" % keyword,
            "vertical": "content",
            "post_search_vertical": None,
            "filters": {
                "filter_author": "stories-feed-friends",
                "filter_author_enabled": "true"
            },
            "has_chrono_sort": False,
            "query_analysis": None,
            "subrequest_disabled": False,
            "token_role": "NONE",
            "preloaded_story_ids": [],
            "extra_data": None,
            "disable_main_browse_unicorn": False,
            "entry_point_scope": None,
            "entry_point_surface": None,
            "squashed_ent_ids": [],
            "source_session_id": None,
            "preloaded_entity_ids": [],
            "preloaded_entity_type": None,
            "query_source": None
        }
        
        enc_q = {
            "view": "list",
            "encoded_query": json.dumps(sub_query),
            "encoded_title": "",
            "ref": "unknown",
            "logger_source": "www_main",
            "typeahead_sid": "",
            "tl_log": False,
            # "impression_id": "c02624f9",
            "experience_type": "grammar",
            "exclude_ids": None,
            "browse_location": "browse_location:browse",
            "trending_source": None,
            "reaction_surface": None,
            "reaction_session_id": None,
            "ref_path": "/search/str/football/keywords_blended_posts",
            "is_trending": False,
            "topic_id": None,
            "place_id": None,
            "story_id": None,
            "callsite": "browse_ui:init_result_set",
            "has_top_pagelet": True,
            "display_params": {
                "crct": "none",
                "mrss": True
            },
        }
        
        enc_q.update(self._next_page_params)
        
        return {
            'dpr'   : '1',
            'data'  : json.dumps(enc_q),
            '__user': self._fbuser_id,
            '__a'   : '1',
            '__be'  : '1',
            '__pc'  : 'PHASED:DEFAULT',
        }

keyword = input('What industry do you want to find ? : ')
keyword = keyword.strip()
crawler = FbUserListCrawler(
    keyword=keyword,
    email='yyy',
    password='xxx',
)
ids = crawler.crawl_now()
pprint(ids)
