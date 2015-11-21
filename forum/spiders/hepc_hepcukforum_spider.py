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

class ForumsSpider(CrawlSpider):
    name = "hepc_hepcukforum_spider"
    allowed_domains = ["www.hepcukforum.org"]
    start_urls = [
        "http://www.hepcukforum.org/phpBB2/viewforum.php?f=1&sid=da54cd4e2f79318463ea37a3e6c8c61a",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topiclink"]', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="pagination"]/a[contains(text(), "Next")]'
                ), follow=True),
        )


    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 


    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="post"]')
        items = []
        condition = "hep c"
        topic = response.xpath('//table[@class="hdr"][1]//td[@nowrap="nowrap"]/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="name"]/text()').extract_first()
            if item['author']:
                item['author_link'] = ''
                item['condition'] = condition
                item['create_date'] = post.xpath('.//span[@class="postdate"]/text()').extract_first().replace(u'Posted:','').strip()
                item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="postbody"]/text()').extract()))
                # item['tag']=''
                item['topic'] = topic.strip()
                item['url']=url
                items.append(item)
        return items