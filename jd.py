# -*- coding: UTF-8 -*-

from crawler2 import Parser
from pyquery import PyQuery
import re

class JdParser(Parser):
    def parseCategories(self, homepage_content):
        doc = PyQuery(homepage_content)
        categoryInfo = self.newCategory()
        categoryInfo.url = self.merchant.crawlEntryUrl
        categoryInfo.name = '健康监测'
        categoryInfo.parent_categories = ['数码', '智能设备']
        return [categoryInfo]
    
    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc('ul.gl-warp > li.gl-item')
        productList = []
        fw = open("C:/users/administrator/desktop/p.html", 'w')
        fw.write(category_page_content)
        fw.close()
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['name'] = nodeQ('div.p-name > a > em').text()
            productInfo['product_url'] = 'http:' + nodeQ('div.p-name > a').attr('href')
            if not nodeQ('div.p-img > a > img').attr('src'):
                #后50个
                productInfo['img_url'] = 'http:' + nodeQ('div.p-img > a > img').attr('data-lazy-img')
            else:
                #前10个
                productInfo['img_url'] = 'http:' + nodeQ('div.p-img > a > img').attr('src')
            productInfo['sku_id'] = re.findall('([\d]+)\.html', productInfo['product_url'])[0]
            productInfo['reviews'] = nodeQ('div.p-commit > strong > a').text()
            productInfo['price'] = nodeQ('div.p-price > strong.J_price > i').text()
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        if doc('div#J_bottomPage > span.p-num > a.pn-next').attr('href'):
            return 'http:' + doc('div#J_bottomPage > span.p-num > a.pn-next').attr('href')