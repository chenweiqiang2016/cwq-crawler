# -*- coding: utf-8 -*-

"""
该parser仅可用于衣联网女装品类的抓取
current_url设置开始抓取的页面, 当启动多个parser提速时, 可以手动测试
pageCount用于对已抓的页面进行计数, 通常设置为1
PAGE_LIMIT本次抓取预定抓取的总页面数
"""

from crawler2 import Parser
from utils import extractNum
from pyquery import PyQuery
import re

class EellyParser(Parser):
    current_url = 'http://list.eelly.com/s-category-289-page1.html#fastView'
    pageCount = 1
    PAGE_LIMIT = 1500
    def parseCategories(self, content):
        category_info = self.newCategory()
        category_info.name = '女装'
        category_info.url = self.current_url
        return [category_info]
    
    def parseProductsByCategory(self, content, category_info):
        doc = PyQuery(content)
        productList = []
        nodeList = doc('ul#J_search_list > li.list-item')
        for node in nodeList:
            productInfo =self.newProduct()
            nodeQ = PyQuery(node)
            innerNode1 = nodeQ('div.goods-info > div.name > a')
            productInfo['name'] = PyQuery(innerNode1).text().strip()
            productInfo['product_url'] = PyQuery(innerNode1).attr('href')
            productInfo['sku_id'] = self.extractSkuId(productInfo['product_url'])
            productInfo['store_name'] = nodeQ('div.goods-info > p.store > a').text()
            productInfo['store_url'] = nodeQ('div.goods-info > p.store > a').attr('href')
            productInfo['store_credit'] = nodeQ('div.hide-info').find('span.g-credit > img').attr('lazy_src')
            productInfo['store_comment'] = nodeQ('div.hide-info').find('span.g-comment > span').text()
            productInfo['MOQ'] = extractNum(nodeQ('div.goods-info > p[class="both legend-p"] > span').text().strip())
            productInfo['price'] = self.processPrice(nodeQ('div.goods-info > p.price').text())
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        print len(productList)
        return productList
    
    def extractSkuId(self, url):
        results = re.findall('\/([\d]+)\.html', url)
        if results:
            return results[0]
        
    def processPrice(self, priceText):
        results = re.findall('([\d]+\.[\d]+)', priceText)
        if not results or len(results) > 2:
            return priceText
        elif len(results) == 1:
            return results[0]
        else:
            return results[1]
    
    def needProductDetails(self):
        return True
    
    def parseProductDetails(self, content, product_info):
        doc = PyQuery(content)
        product_info['product_score'] = extractNum(doc('li[class="list syn-eval"]').find('p >span').eq(0).text())
        product_info['reviews'] = doc('li[class="list syn-eval"]').find('p >span>a').text()
        image_list = []
        for imgNode in doc('div.img_list > ul > li > a > img'):
            imgNodeQ = PyQuery(imgNode)
            image_list.append(imgNodeQ.attr('bimg'))
#         for imgNode in doc('div#itemDesc > p > img'):
#             imgNodeQ = PyQuery(imgNode)
#             image_list.append(imgNodeQ.attr('src') if imgNodeQ.attr('src') else imgNodeQ.attr('lazy_src'))
        for imgNode in doc('div.goods-view').find('img'):
            imgNodeQ = PyQuery(imgNode)
            image_list.append(imgNodeQ.attr('src') if imgNodeQ.attr('src') else imgNodeQ.attr('lazy_src'))       
        product_info['image_count'] = str(len(image_list))
        print product_info['sku_id'], '>>>', product_info['image_count']
        product_info['img_urls'] = ','.join(filter(None, image_list))
            
    def parseNextPageUrl(self, content):
        if self.pageCount >= self.PAGE_LIMIT:
            return None 
        pageNum = re.findall('page([\d]+)\.html', self.current_url)[0]
        newPageNum = int(pageNum) + 1
        pageStr = 'page' + str(pageNum)
        newPageStr = 'page' + str(newPageNum)
        self.current_url = self.current_url.replace(pageStr, newPageStr)
        self.pageCount =self.pageCount + 1
        print self.current_url
        return self.current_url
    
    def needProductImages(self):
        return True
