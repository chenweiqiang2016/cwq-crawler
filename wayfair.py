# -*- coding: utf-8 -*-

"""
Date: 09/29/2015
"""

from crawler2 import Parser, ProductInfo
import unittest
import re
from pyquery import PyQuery
from utils import extractNum

class WayfairParser(Parser):
    def createCategory(self, menuQ):
        category_info = self.newCategory()
        category_info.name = menuQ.text().replace('»', '').strip()
        category_info.url = menuQ.attr('href')
        return category_info
    
    def parseCategories(self, homepage_content):
        doc = PyQuery(homepage_content)
        categoryList = []
        level1NodeList = doc("div#cms_page_922 > div[class='js-template-display js-template  dept_wrap ']").find("div.topnav")
        for level1Node in level1NodeList:
            level1NodeQ = PyQuery(level1Node)
            level1Name = level1NodeQ.children("div > span[class='js-lego-data lego_text_field '] > a").text().strip()
            if level1Name.upper() in ['GIFTS', 'SALES']: #最后两个品类 不予考虑
                continue
            level2NodeList = level1NodeQ('div[class="nav_link_block_title nav_link_block_text"] > span > a')
            for level2Node in level2NodeList:
                categoryInfo = self.createCategory(PyQuery(level2Node))
                categoryInfo.parent_categories = [level1Name]
                categoryList.append(categoryInfo)
        #前期只是抓一个三级品类 需要扩展为全站
#         category_info = self.newCategory()
#         category_info.name = 'Chandeliers'
#         category_info.parent_categories = ['Lighting', 'Ceiling Lights']
#         category_info.url = 'http://www.wayfair.com/Chandeliers-C215419.html?sortby=1&curpage=7'#'http://www.wayfair.com/Chandeliers-C215419.html?sortby=1&refid=&sku='
#         categoryList.append(category_info)
        return categoryList
    
    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc("div#view_1 > a.productbox")
        productList = []
        for productNode in productNodeList:
            productNodeQ = PyQuery(productNode)
            productInfo = self.newProduct()
            productInfo['name'] = productNodeQ('p[class="sb_prod_name emphasis"]').text()
            productInfo['product_url'] = productNodeQ.attr('href')
            productInfo['img_url'] = productNodeQ("img.blocklevel").attr('src')
            productInfo['reviews'] = extractNum(productNodeQ('div.reviewbox').remove('span').text())
            #没有找到价格 怀疑是JS加载
            #productInfo['price'] = productNodeQ('span.is_price_value').remove('span').text()
            productInfo['sku_id'] = self.extractSkuId(productInfo['product_url'])
            productInfo['label_price'] = productNodeQ('span.wasprice').text().strip()
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList
    
#     @staticmethod
    def extractSkuId(self, url):
        #http://www.wayfair.com/Keurig-K10-Mini-Plus-Brewing-System-K10-KEG1034.html
        results = re.findall('([\w]+)\.html', url)
        if results: #\w是包括_的
            return results[0]
        else:
            return ''

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        nodeAList = doc("span#view_47 > a")
        for nodeA in nodeAList:
            nodeAQ = PyQuery(nodeA)
            if nodeAQ.remove('span').text().strip().lower() == 'next':
                return nodeAQ.attr('href').strip()
        return None
    
    def needProductDetails(self):
        return True

    def parseProductDetails(self, product_page_content, product_info):
        doc = PyQuery(product_page_content)
        product_info['price'] = re.sub('\s', '', doc('span[class="product_price emphasis "]').text())
        #从下面获取的是描述图的小图
        #imgNodeList = doc('div[class="js-carousel-content car_content"] > div > img')
        imgNodeList = doc('div.js-slider-container > div > a > img')
        results = []
        for node in imgNodeList:
            nodeQ = PyQuery(node)
            url = nodeQ.attr('src')
            if url:
                results.append(url)
        product_info['img_urls'] = ', '.join(results)
    
    def needProductImages(self):
        return True
    
class WayfairParserTest(unittest.TestCase):
    def fetch(self, furl, headers={}):
        """写一个最多五次抓取的获得页面内容的方法,以便直接抓取来测试
        """
        import httplib2
        h = httplib2.Http(timeout=30)
        h.follow_redirects = False
        count = 0
        while True:
            count += 1
            response, content = h.request(uri=furl, method="GET", headers=headers)
            if response.status == 200:
                return content
            if count >= 5:
                print "Try %d times, please modify request headers...(%d)" %(count, response.status)
    
    def testFetch(self, url):
#         url = "http://www.wayfair.com"
#         url="http://www.wayfair.com/Coffee-Makers-C419252.html"
        content = self.fetch(url)
        return content
    
#     def testParseCategories(self):
#         wf = WayfairParser()
#         wf.parseCategories(self.testFetch())
        
#     def testParseProductsByCategory(self):
#         wf = WayfairParser()
#         wf.parseProductsByCategory(self.testFetch(), "")

#     def testParseNextPageUrl(self):
#         wf = WayfairParser()
#         wf.parseNextPageUrl(self.testFetch())

    def testParseProductDetails(self):
        wf = WayfairParser()
        wf.parseProductDetails(self.testFetch('http://www.wayfair.com/Zojirushi-Fresh-Brew-Thermal-10-Cup-Coffee-Maker-EC-BD15BA-ZOJ1029.html'), "")      