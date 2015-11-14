# -*- coding: utf-8 -*-

from crawler2 import Parser
from pyquery import PyQuery

class HouzzParser(Parser):
    def parseCategories(self, homepage_content):
        doc = PyQuery(homepage_content)
        nodeList = doc('ul#header-navigation-menu > li.menu-container')
        categoryList = []
        #去除前面三个和后面两个乱七八糟的分类
        validNodeList = nodeList[3:10]
        for node in validNodeList:
            nodeQ = PyQuery(node)
            level1Name = nodeQ.children('a').text()
            level2NodeList = nodeQ.children('div > ul:first > li.indent-child > span')
            for level2Node in level2NodeList:
                level2NodeQ = PyQuery(level2Node)
                categoryInfo = self.newCategory()
                categoryInfo.name = level2NodeQ.text()
                categoryInfo.url = level2NodeQ.attr('href')
                categoryInfo.parent_categories = [level1Name]
                categoryList.append(categoryInfo.formalize())
        return categoryList

    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc('div#browseSpacesContext > div.content-row > div.ic')
        productList = []
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['sku_id'] = nodeQ.attr('objid')
            productInfo['name'] = nodeQ('div[class="photoMeta "] > a.product-title').text()
            productInfo['product_url'] = nodeQ('div[class="photoMeta "] > a.product-title').attr('href')
            productInfo['price'] = nodeQ('div[class="photoMeta "] > div.price > a').text()
            if nodeQ('div[class="photoMeta "] > div.price > span'):
                productInfo['label_price'] = nodeQ('div[class="photoMeta "] > div.price > span').text()
            productInfo['img_url'] = nodeQ('div.imageArea > a > div > img').attr('src')
            productInfo['likes'] =self.crawler.fetchSocialLikes(productInfo['product_url'])
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList
    
    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        if doc('ul#paginationBar > li > a.next').attr('href'):
            return doc('ul#paginationBar > li > a.next').attr('href')