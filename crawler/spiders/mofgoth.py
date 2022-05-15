# encoding: utf-8
import time
# author：贺佳伊
from bs4 import BeautifulSoup
from utils.util_old import Util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author:贺佳伊
class DemoSpiderSpider(BaseSpider):
    name = 'mofgoth'
    website_id = 1607
    language_id = 0
    start_urls = ['https://www.mof.go.th/th/home']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        start = soup.select_one(
            'body > article > section:nth-child(3) > div > div > div > div.col-md-8 > div > div > div.viewall2f > a:nth-child(2)').get(
            'href')

        news_page_url = start
        #response.meta['category1'] ='News'
        yield Request(url=news_page_url,callback=self.parse_page,meta=response.meta)

    def parse_page(self,response):
        #time.sleep(3)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select('body > article > div.content_insite > div > div > div.all_thum > ul > li')
        for i in a:
            t = i.select_one(
                ' div > div > div.col-md-9.col-sm-8.col-xs-8 > div.detail_news2f > div.title_news > a').get('href')
            t1 = t.split('/')
            t2 = t1[-1].split('-')
            pub_time = t2[0] + '-' + t2[1] + '-' + t2[2] + ' ' + t2[3] + ':' + t2[4] + ':' + t2[5]
        if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(pub_time):
             for i in a:
                news_url = i.select_one(
                ' div > div > div.col-md-9.col-sm-8.col-xs-8 > div.detail_news2f > div.title_news > a').get('href')
                response.meta['abstract'] = i.select_one('div > div > div.col-md-9.col-sm-8.col-xs-8 > div.detail_news2f > div.detail_thum').text
                response.meta['title']=i.select_one(' div > div > div.col-md-9.col-sm-8.col-xs-8 > div.detail_news2f > div.title_news > a').text
                t = i.select_one(
                    ' div > div > div.col-md-9.col-sm-8.col-xs-8 > div.detail_news2f > div.title_news > a').get('href')
                t1 = t.split('/')
                t2 = t1[-1].split('-')
                response.meta['time']=t2[0] + '-' + t2[1] + '-' + t2[2] + ' ' + t2[3] + ':' + t2[4] + ':' + t2[5]
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page_url = soup.select_one('body > article > div.content_insite > div > div > div.pagination2f > ul > li:nth-child(13) > a').get('href')
                yield Request(url=next_page_url, callback=self.parse_page)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        #item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['time']
        item['title'] = response.meta['title']
        try:
            pic_list=[]
            pic_li = soup.select(
                'body > article > div.content_insite > div > div > div.content-gallery2f > div > div')
            for i in pic_li:
                pic_list.append(i.select_one('div>a').get('href'))
            images = pic_list
        except:
            images=None
        item['images'] = images
        body = soup.select('body > article > div.content_insite > div > div > div.content-fullpage2f > p')
        p_list = ''
        for i in body:
            try:
                p_list += (i.text)
            except:
                continue
        item['body'] = p_list
        yield item
        print(item)
