import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "adhd_aaddukproboards_spider"
    allowed_domains = ["proboards.com"]
    start_urls = [
        "http://aadduk.proboards.com/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@class,"thread-link thread")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@class,"board-link board")]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//li[@class="ui-pagination-page ui-pagination-slot"]/a',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//td[@class="unblocked"]')
        items = []
        topic = response.xpath('//h1//text()').extract()[0]
        url = response.url
        condition="adhd"
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[contains(@class,"user-link user")]/text()').extract()[0]
            item['author_link'] = post.xpath('.//a[contains(@class,"user-link user")]/@href').extract()[0]
            item['condition'] = condition
            
            item['create_date'] = post.xpath('.//abbr[@class="time"]/text()').extract()[0]
           
            message = ''.join(post.xpath('.//div[@class="message"]/text()').extract())
            item['post'] = self.cleanText(message)
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
