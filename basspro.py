# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from crawler2 import Parser
from utils import extractNum

class BassproParser(Parser):
    def parseCategories(self, homepage_content):
        doc = pq(homepage_content)
        categoryList = []
        level1NodeList = doc('ul#tab1-nav > li') #全部一级品类
        for level1Node in level1NodeList:
            level1NodeQ = pq(level1Node)
            level1Name = level1NodeQ.children('a').text()
            level2NodeList = level1NodeQ.children('div[class="dropdown tab1"] > div:first > div > div.dropdown-column')
            #每个level2Node形如<h3/><ul/><h3/><ul/><h3/><h3/>
            for level2Node in level2NodeList:
                level2NodeQ = pq(level2Node)
                for element in level2NodeQ.children():
                    elementQ = pq(element)
                    if elementQ.not_('h3'):  #假如为ul元素, 跳过 #elementQ为h3时 结果为[] elementQ为ul时 结果为本身
                        continue
                    if elementQ.next().is_('ul'): #h3后紧接ul
                        level2Name = elementQ('a').text()
                        for level3Node in elementQ.next().children('li'):
                            level3Category = self.newCategory()
                            level3Category.url = 'http://www.basspro.com' + pq(level3Node).children('a').attr('href')
                            level3Category.name = pq(level3Node).children('a').text()
                            level3Category.parent_categories = [level1Name, level2Name]
                            categoryList.append(level3Category)
                    else:
                        level2Category = self.newCategory()
                        level2Category.name = elementQ('a').text()
                        level2Category.url = 'http://www.basspro.com' + elementQ('a').attr('href')
                        level2Category.parent_categories = [level1Name]
#                         if level2Category.name == 'Clearance':
#                             continue
                        categoryList.append(level2Category)
        return categoryList

    def parseProductsByCategory(self, category_page_content, category_info):
        doc = pq(category_page_content)
        productList = []
        productNodeList = doc('div#category-prods > div.product')
        for node in productNodeList:
            nodeQ = pq(node)
            productInfo = self.newProduct()
            productInfo['name'] = nodeQ('div.info > p > a').remove('span').text()
            productInfo['product_url'] = 'http://www.basspro.com' + nodeQ('div.info > p > a').attr('href')
            productInfo['sku_id'] = self.extractSkuId(productInfo['product_url'])
            productInfo['price'] = nodeQ('div.info > div.pricing > p > a.price').text()
            productInfo['reviews'] = extractNum(nodeQ('div.info > div.reviews > p.reviews > a').text())
            productInfo['img_url'] = nodeQ('div.thumb > a > img').attr('src')
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList
    
    def extractSkuId(self, url):
        import re
        if re.findall('product/(\d+)/', url):
            return re.findall('product/(\d+)/', url)[0]
        
    def parseNextPageUrl(self, category_page_content):
        doc = pq(category_page_content)
        if doc('div#endeca-controls-pagination-buttons > a').filter(lambda i: pq(this).text().strip() == '>').attr('href'):
            return 'http://www.basspro.com' + doc('div#endeca-controls-pagination-buttons > a').filter(lambda i: pq(this).text().strip() == '>').attr('href')