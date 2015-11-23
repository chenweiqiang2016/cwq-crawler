# -*- coding: utf-8 -*-

# Non-ASCII character '\xe6' in file <file path>

from crawler2 import Parser
from pyquery import PyQuery

class PetsmartParser(Parser):
    def parseCategories(self, homepage_content):
        '''抓取前六个一级品类'''
        doc = PyQuery(homepage_content)
        categoryList = []
        level1NodeList = doc('ul.pet-main-nav > li.pet-main-nav-item-level1')[:6]
        for node in level1NodeList:
            nodeQ = PyQuery(node)
            level1Name = nodeQ.children('a > span').text()
            level2NodeList = nodeQ.children('div > div > ul > li')[:2] #写死了
            for level2Node in level2NodeList:
                level2NodeQ = PyQuery(level2Node)
                level2Name = level2NodeQ.children('a > span').text()
                level3NodeList = level2NodeQ.children('ul > li > a')
                for level3Node in level3NodeList:
                    level3NodeQ = PyQuery(level3Node)
                    categoryInfo = self.newCategory()
                    categoryInfo.name = level3NodeQ.children('span').text()
                    categoryInfo.url = level3NodeQ.attr('href')
                    categoryInfo.parent_categories = [level1Name, level2Name]
                    categoryList.append(categoryInfo)
        return categoryList
    
    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc('ul.ws-product-list:first > li.hproduct')
        productList = []
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['name'] = nodeQ('h4.ws-product-title').text()
            productInfo['sku_id'] = nodeQ.attr('data-context-sku')
            productInfo['product_url'] = nodeQ('h4').parent('a').attr('href')
            productInfo['img_url'] = nodeQ('div.kor-product-photo > a > img').attr('src')
            productInfo['price'] = nodeQ('div.kor-product-sale-price > span.kor-product-sale-price-value').text()
            productInfo['likes'] = self.crawler.fetchSocialLikes(productInfo['product_url'])
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList
    
    def needProductDetails(self):
        return False
    
    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        url = doc('ul.ws-product-listing-pagination-list > li > a').filter('[title="to next page"]').attr('href')
        return url