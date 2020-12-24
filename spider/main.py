import requests
from bs4 import BeautifulSoup

url = "http://www.baidu.com"
res = requests.get(url)
html = res.content.decode()

bs = BeautifulSoup(html,'lxml')
print(bs)