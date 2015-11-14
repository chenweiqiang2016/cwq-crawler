#-*- coding: utf-8 -*-

from crawler2 import Parser
from pyquery import PyQuery
import re

class BackcountryParser(Parser):
    def parseCategories(self, homepage_content):
        doc = PyQuery(homepage_content)
        #Gifts和Brands li的data-id属性分别为0, 1
        level1NodeList = doc('ul.js-flyout-nav > li').filter(lambda i:PyQuery(this).attr('data-id') > '1')
        categoryList = []
        for level1Node in level1NodeList:
            level1NodeQ = PyQuery(level1Node)
            level1Name = level1NodeQ.children('a').text()
            level2NodeList = doc('div').filter(lambda i, this:PyQuery(this).attr('data-cat-id')==level1NodeQ.attr('data-id')).children('a')
            for level2Node in level2NodeList:
                level2NodeQ = PyQuery(level2Node)
                if not level2NodeQ.attr('class') or not level2NodeQ.text(): #<a class="" href="" data-title=""/>&#13;
                    continue
                categoryInfo = self.newCategory(level2NodeQ.text(), 'http://www.backcountry.com' + level2NodeQ.attr('href'), [level1Name])
                categoryList.append(categoryInfo)
        return categoryList
                
    def parseProductsByCategory(self, category_page_content, category_info):
        if PyQuery(category_page_content)('section.main').find('a').filter(lambda i:PyQuery(this).text().strip()=='View all').eq(0).attr('href'):
            category_info.url = 'http://www.backcountry.com' + PyQuery(category_page_content)('section.main').find('a').filter(lambda i:PyQuery(this).text().strip()=='View all').eq(0).attr('href')
            category_page_content = self.crawler.fetchCategoryPageContent(category_info.url)
        productNodeList = PyQuery(category_page_content)('div#products > div.product')
        productList = []
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['name'] = nodeQ.children('a').attr('title')
            productInfo['product_url'] = 'http://www.backcountry.com' + nodeQ.children('a').attr('href')
            productInfo['img_url'] = nodeQ.children('a > div.ui-pl-img > img[itemprop="image"]').attr('src')
            if not productInfo['img_url']:
                productInfo['img_url'] = nodeQ.children('a > div.ui-pl-img > img[itemprop="image"]').attr('data-src')
            productInfo['img_url'] = "http:" + productInfo['img_url']
            spanList = nodeQ('div.ui-pl-offers > span.ui-pl-pricing > span')
            if len(spanList) <= 2: #价格区间是两个span
                productInfo['price'] = PyQuery(spanList).text().replace(' ', '')
            else:
                productInfo['price'] = PyQuery(spanList).eq(1).text()
                productInfo['label_price'] = PyQuery(spanList).eq(2).text()
            productInfo['sku_id'] = re.findall("skid=([\w-]+)&", productInfo['product_url'])[0] if re.findall("skid=([\w-]+)&", productInfo['product_url']) else ''
            productInfo['reviews'] = nodeQ('div.ui-pl-reviews > span[itemprop="ratingCount"]').text()
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        if doc('section.main').find('a').filter(lambda i:PyQuery(this).text().strip()=='View all').eq(0).attr('href'):
            url = 'http://www.backcountry.com' + doc('section.main').find('a').filter(lambda i:PyQuery(this).text().strip()=='View all').eq(0).attr('href')
            new_page_content = self.crawler.fetchCategoryPageContent(url)
            doc = PyQuery(new_page_content)
        if doc('div.pag > ul > li.pag-next > a').attr('href'):
            return 'http://www.backcountry.com' + doc('div.pag > ul > li.pag-next > a').attr('href')

