from crawler.spiders import BaseSpider

# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re

#将爬虫类名和name字段改成对应的网站名
class aajkaSpider(BaseSpider):
    name = 'aajka'
    website_id = 966  # 网站的id(必填)
    language_id = 1930  # 所用语言的id
    start_urls = ['https://aajka-samachar.in/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    

    def parse(self, response):
        soup = BeautifulSoup(response.text)
        for i in soup.select('#categories-6 a'):
            yield Request(i.attrs['href'], callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text)
        flag = True
        for i in soup.select('.jeg_inner_content article .jeg_meta_date a'):
            date = Util.format_time2(i.text)
            if self.time == None or Util.format_time3(date) >= int(self.time):
                yield Request(i.attrs['href'], callback=self.parse_detail, meta={'date':date})
            else:
                flag = False
                self.logger.info("时间截止")
                break
        if flag:
            try:
                yield Request(soup.select('.page_nav.next')[0].attrs['href'], callback=self.parse_category)
            except:
                pass

    def parse_detail(self, response):
        html = BeautifulSoup(response.text)
        item = NewsItem()
        item['title'] = html.select('.jeg_post_title')[0].text
        categorylist = html.select('#breadcrumbs > span a')
        item['category1'] = categorylist[-2].text
        item['category2'] = categorylist[-1].text
        item['body'] = ''
        for i in html.select('.content-inner > p'):
            item['body'] += (i.text+'\n')
        if html.select('.content-inner > p') != []:
            item['abstract'] = html.select('.content-inner > p')[0].text
        item['pub_time'] = response.meta['date']
        if html.select('.jeg_featured.featured_image a') != []:
            item['images'] = [html.select('.jeg_featured.featured_image a')[0].attrs['href'],]
        yield item
