import json
from pprint import pprint
import requests
from bs4 import BeautifulSoup as BS
# import facebook

class FbBaseCrawler(object):
    
    default_headers = {
        'Accept'                    :'*/*',
        'Cache-Control'             :'no-cache',
        'upgrade-insecure-requests' :'1',
        'User-Agent'                :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Chrome/62.0.3202.94 Safari/537.36'
    }
    
    
    def __init__(self,email,password,users_fbid:list=None):
        self.r              = requests.Session()
        self._user          = email
        self._pass          = password
        self._users_fbid    = users_fbid or []

    def _export_to_csv(self,data):
        import csv
        with open('data_output.csv', 'w') as csv_file:
            fieldnames = ['name','email','job', 'address', 'phone', 'website']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for dat in data:
                writer.writerow(dat)

    
    
    def _get(self,url,params=None,headers=None,cookies=None):
        if params is None:
            params = {}
        if cookies is None:
            cookies = {}
        h=self.default_headers
        if headers:
            h.update(headers)
        return self.r.get(url,params=params,headers=h,cookies=cookies,timeout=10)
    
    
    def _post(self,url,params=None,data=None,headers=None):
        h=self.default_headers
        if headers is not None:
            h.update(headers)
        return self.r.post(url,params=params,data=data,headers=h,allow_redirects=False,timeout=10)
    
    def _fblink(self,link):
        return 'https://www.facebook.com%s' % str(link)
    
    def parser(self, html):
        return BS(html, 'html.parser')
    
    def _login_fb(self):
        
        print('Fresh login')
        try:
            self._get('https://www.facebook.com')
            data = {
                'email': self._user,
                'pass': self._pass,
            }
            login = self._post('https://www.facebook.com/login.php?login_attempt=1&amp;lwv=110', data=data, headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            })
        except Exception as e:
            print('Error login')
            raise e
        self._fbuser_id = self.r.cookies.get('c_user')
        return login.status_code == 302 and self._fbuser_id
    
    