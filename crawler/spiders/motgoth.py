# encoding: utf-8
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
class DemoSpiderSpider(BaseSpider):
    name = 'motgoth'
    website_id = 1258
    language_id = 1866
    start_urls = ['https://www.mot.go.th/motnews.html']

    def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        start = soup.select_one('#wrapper > div.main-content > div.content > div.fullpage > div:nth-child(1) > h2 > span > a').get('href')
        news_page_url = start
        response.meta['category1'] = 'ศูนย์รวมข่าวคมนาคม'
        yield Request(url=news_page_url,callback=self.parse_page,meta=response.meta)

    def parse_page(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        news_page = soup.select_one('body > section:nth-child(6) > div ')
        flag = True
        a = news_page.select('.card-deck > div')
        for i in a:
            t = i.select_one('div>div>a>small.text-muted')
            for time in t:
                time = time.text.split(' ')
                pub_time = str(int(time[2]) - 543) + '-' + mouth[time[1]].rjust(2, '0') + '-' + time[0].rjust(2,'0') + ' 00:00:00'
                response.meta['time']=pub_time
        if self.time is None or int(self.time)<DateUtil.formate_time2time_stamp(pub_time):
            for i in a:
                news_url='https://www.dpwh.gov.ph' + i.select('div')[2].select_one('a').get('href')
                response.meta['abstract'] = i.select_one(' div.card-body > a > h5').text
                yield Request(url=news_url,callback=self.parse_item,meta=response.meta)
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page_url='https://www.mots.go.th/' +soup.select_one('body > section:nth-child(6) > div > div.col-lg-12.pl-0.pr-0.pt-5 > nav > ul > li:nth-child(9) > a').get('href')
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = ' รายการข่าวภารกิจผู้บริหาร'
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
