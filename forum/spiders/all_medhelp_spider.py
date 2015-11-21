# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging
import string
import time

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "all_medhelp_spider"
    allowed_domains = ["www.medhelp.org"]
    start_urls = [
        "http://www.medhelp.org/forums/Epilepsy/show/235",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="fonts_resizable_subject subject_title "]/a',
                    canonicalize=False,
                ), callback='parsePostsList'),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@id="pagination_nav"]/a[@class="msg_next_page"]',
                    canonicalize=False,
                ), follow=True),
        )


    def cleanText(self,text, printableOnly =True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if printableOnly:
            return filter(lambda x: x in string.printable, text)
        return text

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        condition=sel.xpath('//*[@id="community_header"]/div[1]/a[2]/text()').extract_first()
        posts = sel.xpath('//div[@class="post_message_container"]')
        items = []
        topic = response.xpath('//div[@class="question_title"]/text()').extract_first()
        url = response.url
        cnt =0
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="post_byline"]/a/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="post_byline"]/a/@href').extract_first()
            item['condition']=condition.lower()
            epoch_time = post.xpath("//span[contains(@class,'byline_date')]/@data-timestamp").extract()[0]
            item['create_date']= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(epoch_time)))
            item['post'] =self.cleanText(" ".join(post.xpath('.//div[@class="post_message fonts_resizable"]/text()').extract()))
            item['topic'] = self.cleanText(topic)
            item['url']=url
            cnt+=1
            items.append(item)
        return items