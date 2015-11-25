# -*- coding: utf-8 -*-

from crawler2 import Parser
from pyquery import PyQuery
from utils import extractNum

class BestwigoutletParser(Parser):
    """抓取http://www.bestwigoutlet.com/most-popular-wigs.html页面下的50个商品
    """
    def parseCategories(self, homepaege_content):
        category_info = self.newCategory()
        category_info.name = 'Most Popular'
        category_info.url =self.merchant.crawlEntryUrl
        return [category_info]
    
    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc('table.item')
        productList = []
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
            productInfo['product_url'] = self.merchant.filteruri(nodeQ.find('a.list-link').attr('href'))
            productList.append(productInfo)
        return productList

    def needProductDetails(self):
        return True

    def parseProductDetails(self, product_page_content, product_info):
        doc = PyQuery(product_page_content)
        product_info['name'] = doc('h1#div_product_name').text()
        product_info['sku_id'] = doc('span#div_product_itemno').text()
        product_info['price'] = doc('span#div_product_price').text()
        product_info['label_price'] = doc('span#div_retail_price').text()
        product_info['img_url'] = self.merchant.filteruri(doc('img#target_img').attr('src'))
        #获取reviews数目
        product_info['reviews'] = '0'
        bNodeList = doc('b')
        for item in bNodeList:
            text = PyQuery(item).text()
            if text.startswith("Customer Reviews"):
                product_info['reviews'] = extractNum(text)
                break
        #获取品类路径
        nodeList = doc('a.nav-location')
        if PyQuery(nodeList[0]).text().strip() == 'Home':
            nodeList = nodeList[1:]
        for i, node in enumerate(nodeList):
            product_info['level' + str(i+1) + '_category'] = PyQuery(node).text().strip()