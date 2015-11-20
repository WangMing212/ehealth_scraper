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

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_cancer_spider"
    allowed_domains = ["csn.cancer.org"]
    start_urls = [
        "https://csn.cancer.org/forum/129",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="title"]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@title="Go to next page"]'
                ), follow=True),
        )


    def cleanText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()


    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@id="comments"]/table')
        items = []
        condition="lung cancer"
        topic = response.xpath('//div[@class="left-corner"]/h2/text()').extract_first()
        url = response.url

        item = PostItemsList()
        item['author'] = response.xpath('.//table[@class="node node-forum"]//div[@class="author"]/text()').extract_first()
        item['author_link'] = ''
        item['condition'] = condition
        item['create_date'] = response.xpath('.//table[@class="node node-forum"]//div[@class="date"]/span/text()').extract_first()
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('.//table[@class="node node-forum"]//div[@class="content"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="author"]/text()').extract_first()
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = post.xpath('.//div[@class="date"]/span/text()').extract_first()
            item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="content"]/p/text()').extract()))
            # item['tag']='epilepsy'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
