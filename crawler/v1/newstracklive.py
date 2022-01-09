from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
import requests
import socket

def time_font(time_past):
    #%Y-%m-%d %H:%M:%S
    time_past = time_past.strip()
    year = time_past.split(' ')[2]
    month = time_past.split(' ')[0]
    day = time_past.split(' ')[1]
    second = '00'
    hour = time_past.split(' ')[3].split(":")[0]
    minute = time_past.split(' ')[3].split(":")[1]
    half = time_past.split(' ')[4]
    if half == 'PM':
        hour = int(hour) + 11
    if month == 'Jan':
        month = '01'
    elif month == 'Feb':
        month = '02'
    elif month == 'Mar':
        month = '03'
    elif month == 'Apr':
        month = '04'
    elif month == 'May':
        month = '05'
    elif month == 'Jun':
        month = '06'
    elif month == 'Jul':
        month = '07'
    elif month == 'Aug':
        month = '08'
    elif month == 'Sep':
        month = '09'
    elif month == 'Oct':
        month = '10'
    elif month == 'Nov':
        month = '11'
    else:
        month = '12'
    return year + '-' + month + '-' + day + ' ' + str(hour) + ':' + month + ':' + second

class newstracklive(BaseSpider):
    name = 'newstracklive'
    website_id = 1134  # 网站的id(必填)
    language_id = 1740  # 所用语言的id
    start_urls = ['https://www.newstracklive.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response, **kwargs):
        html = BeautifulSoup(response.text, 'lxml')
        page_list = []
        # 解析一级目录
        test_page_list = html.select('div.collapse.navbar-collapse ul li')
        for i in range(3):
            page_list.append(test_page_list[i].find('a').get('href'))
        test_page_list.clear()
        test_page_list.extend(
            html.select('div.collapse.navbar-collapse ul li.dropdown ul.dropdown-menu.text-capitalize li'))
        for test_page in test_page_list:
            page_list.append(test_page.find('a').get('href'))
        for i in page_list:
            yield Request(i , callback=self.parse_2)

    def parse_2(self , response ,  **kwargs):
        socket.setdefaulttimeout(30)
        page_soup = BeautifulSoup(response.text, 'lxml')
        category1 = page_soup.select('div.main-title-outer.pull-left div.main-title')[0].text.strip()
        item = NewsItem()
        item['category1'] = category1
        item['category2'] = category1
        for i in page_soup.select('div.col-md-4.col-sm-8.col-xs-16 div.topic.nt_topic a'):
            yield Request(i.attrs['href'],callback=self.parse_3,meta={'item':item})
        if page_soup.select('div.ntdv_pagination li')[-1].find('a').attrs['href']:
            next_page = response.url.split('?')[0] + page_soup.select('div.ntdv_pagination li')[-1].find('a').attrs['href']
            last_news_url = page_soup.select('div.col-md-4.col-sm-8.col-xs-16 div.topic.nt_topic a')[-1].attrs['href']
            last_time = time_font(BeautifulSoup(requests.get(last_news_url).text).select('div.time')[0].text)
            if self.time == None or Util.format_time3(last_time) >= int(self.time):# 截止功能
                #下一页
                yield Request(next_page,callback=self.parse_2)
            else:
                self.logger.info('时间截止')

    def parse_3(self, response):
        item = response.meta['item']
        new_soup = BeautifulSoup(response.text)
        try:
            item['title'] = new_soup.select('div.sec-topic.nt_detailview.col-sm-16.wow.fadeInDown.animated div.col-sm-16.sec-info > h1')[0].text
            item['pub_time'] = time_font(new_soup.select('div.text-danger.sub-info-bordered div.time')[0].text) if len(new_soup.select('div.text-danger.sub-info-bordered div.time')) else Util.format_time()
            item['body'] = ''
            if len(new_soup.select('.col-sm-16.sec-info p')):
                for bodys in new_soup.select('.col-sm-16.sec-info p'):
                    item['body'] += bodys.text
            else:
                for bodys in new_soup.select('.carousel-caption p'):
                    item['body'] += bodys.text
            item['abstract'] = new_soup.select('.col-sm-16.sec-info p')[0].text if len(new_soup.select('.col-sm-16.sec-info p')) else new_soup.select_one('.carousel-caption p')
            item['images'] = []
            if len(new_soup.select(
                    'div.sec-topic.nt_detailview.col-sm-16.wow.fadeInDown.animated div.ntdv_imgcon > img')):
                new_images_list = new_soup.select(
                    'div.sec-topic.nt_detailview.col-sm-16.wow.fadeInDown.animated div.ntdv_imgcon > img')
                for new_images in new_images_list:
                    item['images'].append(new_images.get('src'))
        except:
            pass
        yield item