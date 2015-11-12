#-*- coding: utf-8 -*-
from crawler2 import Parser
from pyquery import PyQuery

class TvcmallParser(Parser):
    def parseCategories(self, homepage_content): #目前是抓的Bestselling目录下商品
        category_info = self.newCategory()
        category_info.name = "Bestselling" #仅仅是个标识, 不用于商品
        category_info.url = "http://www.tvc-mall.com/Catalog/BestDeals"
        return [category_info]

    def parseProductsByCategory(self, category_page_content, category_info):
        productList = []
        doc = PyQuery(category_page_content)
        productNodeList = doc('div.new_product > div > ul > li')
        for node in productNodeList:
            productInfo = self.newProduct()
            nodeQ = PyQuery(node)
            productInfo['name'] = nodeQ('div.cp_title > a').text()
            productInfo['product_url'] = 'http://www.tvc-mall.com' + nodeQ('div.cp_title > a').attr('href')
            productInfo['sku_id'] = nodeQ('div.cp_title > a').attr('sku')
            productInfo['reviews'] = nodeQ('span.detail_reviews > a').text()
            productInfo['img_url'] = nodeQ('div > a > img').attr('data-src')
            productInfo['price'] = nodeQ("p > span[name='p_curprice']").text()
            productList.append(productInfo)
        return productList

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        return self.merchant.crawlEntryUrl + doc('div.pagebar > a:last').attr('href')
    
    def needProductDetails(self):
        return True #需要到单品页面抓取品类路径
    
    def parseProductDetails(self, product_page_content, product_info):
        nodeList = PyQuery(product_page_content)('div.location > a')
        for i, node in enumerate(nodeList):
            levelName = 'level' + str(i+1) + '_category'
            product_info[levelName] = PyQuery(node).text().strip()
        