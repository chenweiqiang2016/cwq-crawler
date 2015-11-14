# -*- coding: utf-8 -*-

# 抓取品类页面的headers为空 
# 网站不稳定, 品类的第二页打不开

from crawler2 import Parser
from utils import extractNum
from pyquery import PyQuery
import re

class GearbestParser(Parser):
    def parseCategories(self, homepage_content):
        """首页可以看到二级品类, 按照要求只抓取一级品类"""
        doc = PyQuery(homepage_content)
        level1NodeList = doc('div#js_nav_list > ul > li > a')
        categoryList = []
        for level1Node in level1NodeList:
            level1NodeQ = PyQuery(level1Node)
            categoryInfo = self.newCategory()
            categoryInfo.name = level1NodeQ.text()
            categoryInfo.url = level1NodeQ.attr('href')
            categoryList.append(categoryInfo)
        return categoryList

    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList = doc('ul#catePageList > li')
        productList = []
        productNodeList = productNodeList[:36] #最后一个是next page方框按钮
        for node in productNodeList:
            nodeQ, productInfo = PyQuery(node), self.newProduct()
            productInfo['name'] = nodeQ('p.all_proNam > a').attr('title')
            productInfo['product_url'] = nodeQ('p.all_proNam > a').attr('href')
            productInfo['sku_id'] = re.findall('p_(\d+)\.html', productInfo['product_url'])[0] if re.findall('p_(\d+)\.html', productInfo['product_url']) else ''
            productInfo['img_url'] = nodeQ('p.all_proImg > a.proImg_a > img').attr('data-original')
            productInfo['price'] = nodeQ('div.all_price > span.my_shop_price').attr('orgp')
            productInfo['reviews'] = extractNum(nodeQ('div.all_proStart > a').filter(lambda i: PyQuery(this).attr('title')=='Customer Reviews').text())
            productInfo['likes'] = nodeQ('i.addFavorNum').text()
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        if doc('div.pages > p.listspan > a.next').attr('href'):
            return 'http://www.gearbest.com' + doc('div.pages > p.listspan > a.next').attr('href')

