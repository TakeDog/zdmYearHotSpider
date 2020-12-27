# -*- coding:utf-8 -*- #
import requests
from bs4 import BeautifulSoup
import json
import re
import time
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

class YearSpider(object):

    def __init__(self,person='',stype=0):
        """
        pserson_str:候选人列表，在网页粘贴复制即可。
        stype:爬取类型。0-全部，1-点赞，2-收藏，3-评论，4-打赏
        """
        if person:
            person = person.split('、')
            self.person_list = [i[1:] for i in person]
        else:
            self.person_list = ''
            #print "请输入字符"
            #exit()
        self.stype = stype
        # print(self.person_list)
        #print json.dumps(a, ensure_ascii=False)   #py3
        #print json.dumps(self.person_list,encoding='UTF-8',ensure_ascii=False)    #py2

    def getContent(self,url,extra_headers=''):
        """
        发送请求，获得网页内容字符串
        """
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}

        if extra_headers :
            headers = {**headers,**extra_headers}

        res = requests.get(url,headers=headers)
        html = res.content.decode()
        return html
    
    def getHtmlBs(self,url,extra_headers=''):
        """
        发送请求，并且获得bs对象
        """
        html = self.getContent(url,extra_headers)
        bs = BeautifulSoup(html,'lxml')
        return bs
        
    def getUserLinkByName(self,user_name):
        """
        根据用户名，获取用户主页文章URL
        """
        find_user_url = "https://search.smzdm.com/?c=zhiyou&s=" + user_name + "&v=b"
        bs = self.getHtmlBs(find_user_url)
        
        user_home_urls = bs.find_all('a',class_='search-user-title')

        user_home_url = ''
        for user in user_home_urls:
            if user.string == user_name:
                user_home_url = user['href'] + 'article/'
                break

        #user_list = bs.find
        return user_home_url

    def time_data(self,time_sj):                #传入单个时间比如'2019-8-01 00:00:00'，类型为str
        """
        用于时间转时间戳
        """
        data_sj = time.strptime(time_sj,"%Y-%m-%d %H:%M:%S")       #定义格式
        time_int = int(time.mktime(data_sj))
        return time_int             #返回传入时间的时间戳，类型为int

    def getArticleHot(self,bs,limit_time=''):
        info = {'like':0,'collect':0,'comment':0,'reward':0,'hot':0,'count':0}
        article_list = bs.select(".pandect-content-title")
        #for i in article_list:
        #    article_url = i.find('a')['href']
        #https://post.smzdm.com/p/aekw8v6m/ -- 无打赏

        article_url = 'https://post.smzdm.com/p/apz0qkg9/'
        reward_url = 'https://zhiyou.smzdm.com/user/shang/jsonp_shang_list?channel_id=11&article_id=71219346&get_total=1&page=1&limit=1'
        extra_headers = {'Host':'zhiyou.smzdm.com','Referer':'https://post.smzdm.com/'}

        article_bs = self.getHtmlBs(article_url)    #获取文章HTML
        reward_json = self.getContent(reward_url,extra_headers)    #获取文章打赏数据
        reward_data = json.loads(reward_json)
        reward = int(reward_data['data']['total'])

        span_list = article_bs.select('.recommend-tab>.xilie>span')
        for idx,val in enumerate(span_list):
            if idx == 0:
                add_time = self.time_data(val.string)
            elif idx == 1:
                like = int(re.findall(r'\d+',val.string)[0])
            elif idx == 2:
                collect = int(re.findall(r'\d+',val.string)[0])
            elif idx == 3:
                comment = int(re.findall(r'\d+',val.string)[0])
        
        info['like'] += like
        info['collect'] += collect
        info['comment'] += comment
        info['reward'] += reward
        info['hot'] += like + collect + comment + reward
        info['count']+=1

        print(info)
        #reward_bs = article_bs.find_all('a',class_='gratuity-num')
        #print(reward_data['data']['total'])

    def getUserHot(self,user_name,limit_time=''):
        """
        根据用户名，获取用户所有文章热度
        """
        user_home_url = self.getUserLinkByName(user_name)
        bs = self.getHtmlBs(user_home_url)
        pages = bs.select(".pagination>li>a")
        bs_len = len(pages)

        self.getArticleHot(bs)
        # article_list = bs.find_all("div",class_='pandect-content-small')
        # return len(article_list)
        #可能的最大遍历次数
        #max_page = pages[-3].string if bs_len else 1
        
        #第一页热度：
        #for i in range(int(max_page)):
        #    print(i)
    
    
        #info = {'like':0,'collect':0,'comment':0,'reward':0}
        #article_list = bs.find_all("div",class_='pandect-content-small')
        #return len(article_list)

    def a():
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
        url = "http://www.baidu.com"
        res = requests.get(url,headers=headers)
        html = res.content().decode()

        #bs = BeautifulSoup(html,'lxml')
        #video_str = bs.select("a[class='lb']")
        #print(video_str[0].string)

def main():
    #person = input('请输入达人字符：')
    #与秋作伴   我是小心心  金色浪花
    spider = YearSpider()
    str = spider.getUserHot('与秋作伴')
    #print(str)

if __name__ == "__main__":
    main()