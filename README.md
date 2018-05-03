# Fb_crawler



## *TEST FOR FACEBOOK PLACES CRAWL
Install dependences:
`pip3 install -r ./requirements.txt`

Put in you Facebook account info: (at the end of *`facebook_listplace_crawler.py`)
```python
crawler = FbPageListCrawler(
    ...
    email='yyy', # your account
    password='xxx', # your password
)
```
Run:

`python3 ./facebook_listplace_crawler.py`


## DEPPRECATED(*)
## Test run
Install dependences:
`pip3 install -r ./requirements.txt`

Put in you Facebook account info: (at the end of `facebook_listuser_crawler.py`)
```python
crawler = FbUserListCrawler(
    ...
    email='yyy', # your account
    password='xxx', # your password
)
```
Run:

`python3 ./facebook_listuser_crawler.py`
