# -*- coding:utf-8 -*- #
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import re
import time
import xlwt
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

class YearSpider(object):

    #def __init__(self,person='',stype=0):
        
        

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

    def date2time(self,time_sj):                #传入单个时间比如'2019-8-01 00:00:00'，类型为str
        """
        用于时间转时间戳
        """
        data_sj = time.strptime(time_sj,"%Y-%m-%d %H:%M:%S")       #定义格式
        time_int = int(time.mktime(data_sj))
        return time_int             #返回传入时间的时间戳，类型为int

    def getArticleHot(self,page_url,begin_date='',over_date=''):    
        """
        获取一页中的所有热度
        """
        info = {'like':0,'collect':0,'comment':0,'reward':0,'hot':0,'count':0}

        bs = self.getHtmlBs(page_url)

        article_list = bs.select(".pandect-content-title")

        begin_time = self.date2time(begin_date+' 00:00:00') if begin_date else 1 #begin_date有值就转值，没值用1970/1/1 8:0:1的时间戳。
        over_time = self.date2time(over_date+' 23:59:59') if over_date else self.date2time('2077-01-01 23:59:59') #over_date有值就转值，没值用2077-01-01 23:59:59的时间戳。
        #exit_flag = False
        # print(article_list)
        for i in tqdm(article_list,desc='Processing') :
            article_url = i.find('a')['href']
            article_bs = self.getHtmlBs(article_url)    #获取文章HTML
            span_list = article_bs.select('.recommend-tab>.xilie>span')
            for idx,val in enumerate(span_list):
                if idx == 0:
                    add_time = self.date2time(val.string)
                elif idx == 1:
                    like = int(re.findall(r'\d+',val.string)[0])
                elif idx == 2:
                    collect = int(re.findall(r'\d+',val.string)[0])
                elif idx == 3:
                    comment = int(re.findall(r'\d+',val.string)[0])
            
            if add_time < begin_time :
                return {'exit_flag' : True , 'data':info}
            else :
                if add_time <= over_time:
                    #获取文章打赏数据
                    article_id = article_bs.find('input',id='rewardOptions')['data-articleid']
                    reward_url = 'https://zhiyou.smzdm.com/user/shang/jsonp_shang_list?channel_id=11&article_id='+article_id+'&get_total=1&page=1&limit=1'
                    extra_headers = {'Host':'zhiyou.smzdm.com','Referer':'https://post.smzdm.com/'}
                    reward_json = self.getContent(reward_url,extra_headers)    #获取文章打赏数据
                    reward_data = json.loads(reward_json)
                    reward = int(reward_data['data']['total'])

                    #统计数据
                    info['like'] += like
                    info['collect'] += collect
                    info['comment'] += comment
                    info['reward'] += reward
                    info['hot'] += like + collect + comment + reward
                    info['count']+=1
                else :
                    continue

        return {'exit_flag' : False , 'data' : info}

    def getUserHot(self,user_name,begin_date='',over_date=''):  #获取单人的所有热度
        """
        根据用户名，获取该用户所有文章热度
        """
        user_home_url = self.getUserLinkByName(user_name)
        
        bs = self.getHtmlBs(user_home_url)
        pages = bs.select(".pagination>li>a")
        bs_len = len(pages)

        #user_hot = self.getUserHotForOne(bs,begin_date,over_date)
        #user_hot['user_name'] = user_name

        #可能的最大遍历次数
        max_page = pages[-3].string if bs_len else 1
        
        info = {'user_name':user_name,'like':0,'collect':0,'comment':0,'reward':0,'hot':0,'count':0}
        for i in range(int(max_page)):
            page_url = user_home_url + 'p' + str(i+1)
            res = self.getArticleHot(page_url,begin_date,over_date)

            exit_flag = res['exit_flag']
            hot_info = res['data']

            info['like'] += hot_info['like']
            info['collect'] += hot_info['collect']
            info['comment'] += hot_info['comment']
            info['reward'] += hot_info['reward']
            info['hot'] += hot_info['hot']
            info['count'] += hot_info['count']

            print('已爬取用户：{'+ user_name + '} 第' + str(i+1) + '页数据')

            if exit_flag :
                return info

        return info

    def run(self,person,begin_date='',over_date=''):    
        """
        启动爬虫，获取数据，导出Excel
        """
        person = person.split('、')
        person_list = [i[1:] for i in person]
        titles = ['用户','点赞','收藏','评论','打赏','总热度','总篇数']
        data = []
        for user_name in person_list : 
            user_hot = self.getUserHot(user_name,begin_date,over_date)
            data.append(user_hot)

        xls = xlwt.Workbook()
        sheet = xls.add_sheet('sample')

        #先写Excel表头
        for tkey,title in enumerate(titles) :
            sheet.write(0, tkey, title)

        #再写Excel数据
        for k,v in enumerate(data):
            row = k+1
            sheet.write(row, 0, v['user_name'])
            sheet.write(row, 1, v['like'])
            sheet.write(row, 2, v['collect'])
            sheet.write(row, 3, v['comment'])
            sheet.write(row, 4, v['reward'])
            sheet.write(row, 5, v['hot'])
            sheet.write(row, 6, v['count'])

        excel_name = begin_date+'至'+over_date+'et_'+str(int(time.time()))+'.xls'
        xls.save(excel_name)
        print('数据已导出，请在当前目录查看。文件名：' + excel_name)

def main():
    print('')
    print("--------------------------------------------------------------")
    print("欢迎使用年度达人热度爬取器V1.0，由于数据量大，爬取过程中请耐心等候。")
    print("--------------------------------------------------------------")
    print('')
    person = input('候选人列表，在网页复制粘贴即可。(如：@zouzoulong、@眼睛君)：')
    begin_date = input('请输入开始时间：')    #时间格式：2020-01-01
    over_date = input('请输入结束时间：')     #时间格式：2020-01-01
    #与秋作伴   我是小心心  金色浪花
    spider = YearSpider()
    spider.run(person,begin_date,over_date)
    

if __name__ == "__main__":
    main()