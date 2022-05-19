# encoding: utf-8
import time

from bs4 import BeautifulSoup
from utils.util_old import Util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
mouth = {
    'มกราคม': '1',
    'กุมภาพันธ์': '2',
    'มีนาคม': '3',
    'เมษายน': '4',
    'พฤษภาคม': '5',
    'มิถุนายน': '6',
    'กรกฎาคม': '7',
    'สิงหาคม': '8',
    'กันยายน': '9',
    'ตุลาคม': '10',
    'พฤศจิกายน': '11',
    'ธันวาคม': '12',
}
#Auther:
class DemoSpiderSpider(BaseSpider):
    name = 'mfagoth'
    website_id = 1609
    language_id = 0
    start_urls = ['https://www.mfa.go.th/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        start=soup.select_one('#__next > div.jsx-1514528881.website-container.lang-th > div.jsx-1514528881 > div > div > div:nth-child(2) > div > a ').get('href')
        news_page_url = 'https://www.mfa.go.th/' + start
        response.meta['category1'] ='ข่าวเด่น'
        response.meta['page']=1
        yield Request(url=news_page_url,callback=self.parse_page,meta=response.meta)

    def parse_page(self,response):
        time.sleep(3)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select(
            '#__next > div.jsx-1514528881.website-container.lang-th > div.jsx-1514528881 > div > div.jsx-1514528881.px-0.col-md-9 > div > div > div.row > div')
        for i in a:
            t = i.select_one(
                ' div > div.jsx-2368373130.content.px-0.py-3.d-flex.flex-column.justify-content-between > div:nth-child(2) > div > div:nth-child(1) > p').text
            ti = t.split(' ')
            pub_time = str(int(ti[2]) - 543) + '-' + mouth[ti[1]].rjust(2, '0') + '-' + ti[0].rjust(2,'0') + ' 00:00:00'
        if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(pub_time):
             for i in a:
                news_url = 'https://www.mfa.go.th/' + i.select_one(' div > div.jsx-2368373130.content.px-0.py-3.d-flex.flex-column.justify-content-between > a').get('href')
                response.meta['title'] = i.select_one(' div > div.jsx-2368373130.content.px-0.py-3.d-flex.flex-column.justify-content-between > a > div').text
                t1 = i.select_one(
                    ' div > div.jsx-2368373130.content.px-0.py-3.d-flex.flex-column.justify-content-between > div:nth-child(2) > div > div:nth-child(1) > p').text
                ti1 = t1.split(' ')
                response.meta['pub_time'] = str(int(ti1[2]) - 543) + '-' + mouth[ti1[1]].rjust(2, '0') + '-' + ti1[0].rjust(2,
                                                                                                        '0') + ' 00:00:00'
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                response.meta['page']=response.meta['page']+1
                next_page_url = 'https://www.mfa.go.th/th/content-category/%E0%B8%82%E0%B9%88%E0%B8%B2%E0%B8%A7%E0%B9%80%E0%B8%94%E0%B9%88%E0%B8%99?p='+str(response.meta['page'])
                yield Request(url=next_page_url, callback=self.parse_page,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        try:
            images = soup.select_one('#newsgallery > div:nth-child(1) > div > div:nth-child(1) > img').get('src')
        except:
            images=None
        item['images'] = images
        title= soup.select_one('body > section:nth-child(6) > div > div.col-lg-12.w-100.p-0.pt-4 > h2 ').text
        item['title'] = title
        body = soup.select('body > section:nth-child(6) > div> div > p.MsoNoSpacing ')
        p_list = []
        for i in body:
            try:
                p_list.append(i.text)
            except:
                continue
        item['body'] = p_list
        yield item