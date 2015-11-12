# -*- coding: utf-8 -*-
from crawler2 import Parser
from pyquery import PyQuery

class MissesDressyParser(Parser):
    def createCategory(self, menuQ):
        category_info = self.newCategory()
        category_info.name = menuQ.text()
        category_info.url = menuQ.attr('href')
        return category_info
    
    def parseCategories(self, homepage_content):
        doc = PyQuery(homepage_content)
        categoryList = []
        nodeList = doc("nav#mnav > ul.nav > li.dropdown > a")
        for node in nodeList:
            categoryInfo = self.createCategory(PyQuery(node))
            categoryList.append(categoryInfo)
        return categoryList

    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productList = []
        #product后面的空格必不可少
        productNodeList = doc('div[class="product "]')#div.ajax-results > div.product
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['name'] = nodeQ('h5 > a').text()
            productInfo['product_url'] = nodeQ('h5 > a').attr('href')
            productInfo['img_url'] = 'http://www.missesdressy.com' + nodeQ('img.standard').attr('src') #a.image_wrapper > img.standard
            productInfo['sku_id'] = self.extractSkuId(productInfo['product_url'])
            productInfo['price'] = nodeQ("div.price_wrap > div.price").text()
            productInfo.set_categories(category_info)
            productList.append(productInfo.formalize())
        return productList
    
    def extractSkuId(self, url):
        import re
        if re.findall("([\d]+)_[\d]+$", url):
            return re.findall("([\d]+)_[\d]+$", url)[0]
        if re.findall("([\da-zA-Z]+)$", url):
            return re.findall("([\da-zA-Z]+)$", url)[0]
    
    def needProductDetails(self):
        return True
        
    def parseProductDetails(self, product_page_content, product_info):
        doc = PyQuery(product_page_content)
        product_info['reviews'] = doc("span.review_qty").text()
        product_info['likes'] = self.crawler.fetchSocialLikes(product_info['product_url'])

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        for liNode in doc('div.pagination:first > ul > li'):
            liNodeQ = PyQuery(liNode)
            if liNodeQ.text().strip().startswith("Next"):
                return liNodeQ.children('a').attr('href')

