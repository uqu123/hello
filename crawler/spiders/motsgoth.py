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
    name = 'motsgoth'
    website_id = 1609
    language_id = 0
    start_urls = ['https://www.mots.go.th/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        start=soup.select_one('body > section:nth-child(13) > div > div > div > div > div > div.col-lg-12.p-0.pt-4.d-flex.justify-content-end > a').get('href')
        news_page_url = 'https://www.mots.go.th/' + start
        response.meta['category1'] ='News'
        yield Request(url=news_page_url,callback=self.parse_page,meta=response.meta)

    def parse_page(self,response):
        time.sleep(3)
        soup=BeautifulSoup(response.text,'lxml')
        news_page = soup.select_one('body > section:nth-child(6) > div ')
        flag = True
        a = news_page.select('.card-deck > div>div>div>a>small.text-muted')
        for i in a:
            t = i.select_one('div.card-footer > a:nth-child(1) > small').text
            ti = t.text.split(' ')
            pub_time = str(int(ti[2]) - 543) + '-' + mouth[ti[1]].rjust(2, '0') + '-' + ti[0].rjust(2,'0') + ' 00:00:00'
        if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(pub_time):
             for i in a:
                news_url = 'https://www.mots.go.th/' + i.select_one('div.card-body > a').get('href')
                response.meta['abstract'] = i.select_one(' div.card-body > a > h5').text
                t = i.select_one('div.card-footer > a:nth-child(1) > small').text
                t1=t.text.split(' ')
                response.meta['time']=str(int(t1[2]) - 543) + '-' + mouth[t1[1]].rjust(2, '0') + '-' + t1[0].rjust(2,'0') + ' 00:00:00'
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page_url = 'https://www.mots.go.th/' + soup.select_one(
                        'body > section:nth-child(6) > div > div.col-lg-12.pl-0.pr-0.pt-5 > nav > ul > li:nth-child(9) > a').get(
                        'href')
                yield Request(url=next_page_url, callback=self.parse_page)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = response.meta['abstract']
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
