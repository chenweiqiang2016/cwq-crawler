# -*- coding: utf-8 -*-

from crawler2 import Parser
from pyquery import PyQuery
import re

class BeverlybeauteParser(Parser):
    def parseCategories(self, homepage_content):
        category_info = self.newCategory()
        category_info.name = 'TOP SELLERS'
        category_info.url = self.merchant.crawlEntryUrl
        return [category_info]

    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc('ul.product_list > li > div.product-container')
        productList = []
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['name'] = nodeQ('h5[itemprop="name"] > a.product-name').text()
            productInfo['product_url'] = nodeQ('h5[itemprop="name"] > a.product-name').attr('href')
            productInfo['price'] = nodeQ('div.price_container > span.price').text()
            productInfo['img_url'] = nodeQ('a.product_img_link > img').attr('src')
            productInfo['sku_id'] = re.findall('/([\d]+)[-]', productInfo['product_url'])[0]
            productInfo['likes'] =self.crawler.fetchSocialLikes(productInfo['product_url'])
            productList.append(productInfo)
        return productList
    
    def needProductDetails(self):
        return True

    def parseProductDetails(self, product_page_content, product_info):
        doc = PyQuery(product_page_content)
        categoryName = doc('ul[itemprop="breadcrumb"] > li:even').eq(1).text() #eq(0)为Home
        product_info['level1_category'] = categoryName
    
    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        if doc('div#pagination_bottom > ul.pagination > li > a[rel="next"]').attr('href'):
#             return self.merchant.filteruri(doc('div#pagination_bottom > ul.pagination > li > a[rel="next"]').attr('href'))
            #换成https, 并且不能加3w
            return "https://beverlybeaute.com" + doc('div#pagination_bottom > ul.pagination > li > a[rel="next"]').attr('href')