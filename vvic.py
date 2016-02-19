# -*- coding: utf-8 -*-


import json
import re
from pyquery import PyQuery
from crawler2 import Parser

class VvicParser(Parser):
    
    current_url = 'http://www.vvic.com/rest/search?currentPage=1&pageSize=50&pid=1&sort=up_time-desc'
    
    def parseCategories(self, homePage_content):
        category_info = self.newCategory()
        category_info.name = u'女装'
        category_info.url = 'http://www.vvic.com/rest/search?currentPage=1&pageSize=50&pid=1&sort=up_time-desc'
        return [category_info]

    def parseProductsByCategory(self, category_page_content, category_info):
        datas = json.loads(category_page_content)
        productNodeList = datas['data']['recordList']
        productList = []
        for node in productNodeList:
            product = self.newProduct()
            product['price'] = node['discount_price']
            product['img_url'] = 'http:' + node['index_img_url']
            product['name'] = node['title']
            product['sku_id'] = node['id']
            product['product_url'] = 'http://www.vvic.com/item.html?id=' + product['sku_id']
            product['store_name'] = node['shop_name']
            product['bname'] = node['bname']
            product['update_time'] = str(node['up_time'])
            product['shop_id'] = str(node['shop_id'])
            product['level1_category'] = category_info.name
            productList.append(product)
        return productList
    
    
    def parseShopDetails(self, shop_api_content, product_info):
        datas = json.loads(shop_api_content)
        product_info['qq'] = str(datas['data']['qq']) if datas['data']['qq'] else ''
        product_info['telephone'] = str(datas['data']['telephone']) if datas['data']['telephone'] else ''
        product_info['marketName'] = datas['data']['marketName']
        product_info['floor'] = str(datas['data']['floor'])
        product_info['position'] = datas['data']['position']
        product_info['supplier_name'] = datas['data']['ww_nickname']
        product_info['update_time'] = datas['data']['update_time']
        product_info['city'] = datas['data']['city']
        product_info['remark'] = datas['data']['remark'].replace('\n', '')
    
    def parseItemDetails(self, item_api_content, product_info):
        datas = json.loads(item_api_content)
        #2016-02-17新增desc图片url的提取
#         for xnode in descQ.children('p > img'):
#             imageNodeList.append(PyQuery(xnode).attr('src'))
#         innerQ = PyQuery(descQ.children('table > tbody').eq(-1))
#         flag=False
#         for item in innerQ.children('tr > td'):
#             itemQ = PyQuery(item)
#             if flag:
#                 imgNodeList = itemQ('tr > td > p > img')
#                 for imgNode in imgNodeList:
#                     print PyQuery(imgNode).attr('src')
#                     imageNodeList.append(PyQuery(imgNode).attr('src'))
#                 break
#             if itemQ.children('img') and itemQ.children('img').attr('src') == 'https://img.alicdn.com/imgextra/i3/740135687/TB2kXgRkXXXXXcoXpXXXXXXXXXX_!!740135687.jpg':
#                 flag = True
        product_info['raw_imgs'] = datas['data']['imgs'].strip()        
        #处理一下
        aList = product_info['raw_imgs'].split(',')
        bList = []
        for item in aList:
            bList.append('http:' + item.strip())
        if product_info['img_url'] not in bList:
            bList.append(product_info['img_url'])
        #增加描述图信息提取
        desc = datas['data']['desc']
        for item in PyQuery(desc).find('img'):
            if PyQuery(item).attr('src') and PyQuery(item).attr('src').strip() not in bList:
                bList.append(PyQuery(item).attr('src'))
        
        product_info['imgs'] = ', '.join(bList)
        product_info['size'] = datas['data']['size']
        if datas['data']['up_time']:
            product_info['update_time'] = datas['data']['up_time']
    
    def parseNextPageUrl(self, parseNextPageUrl):
        if re.findall('currentPage=([\d]+)&', self.current_url):
            num = re.findall('currentPage=([\d]+)&', self.current_url)[0]
            self.current_url = self.current_url.replace('currentPage='+str(num), 'currentPage='+str(int(num)+1))
            return self.current_url

    def needProductDetails(self):
        return True
    
#############################之前写过一次从审查元素得到的解析方法,以备不时之需############################
# -*- coding: utf-8 -*-

# import re
# import datetime
# from pyquery import PyQuery
# from crawler2 import Parser
# 
# class VvicParser(Parser):
#     
#     current_url = 'http://www.vvic.com/list.html?pageSize=50&pid=1&sort=up_time-desc#jump' #初始值
#     
#     def parseCategories(self, homepage_content):
#         categoryInfo = self.newCategory()
#         categoryInfo.name = '女装'
#         categoryInfo.url = 'http://www.vvic.com/list.html?pageSize=50&pid=1&sort=up_time-desc#jump'            
#         return [categoryInfo]
# 
#     def parseProductsByCategory(self, page_content, category_info):
#         doc = PyQuery(page_content)
#         productList, productNodeList = [], doc('ul.clearfix > li.item')
#         for node in productNodeList:
#             try:
#                 productInfo, nodeQ = self.newProduct(), PyQuery(node)
#                 productInfo['name'] = nodeQ('div.title > a').attr('title')
#                 productInfo['product_url'] = nodeQ('div.title > a').attr('href')
#                 productInfo['shop_name'] = nodeQ('div.foot > div.shop-name > a').text()
#                 productInfo['shop_url'] = nodeQ('div.foot > div.shop-name > a').attr('href')
#                 productInfo['price'] = nodeQ('div.price').remove('span').text()
#                 productInfo['on_time'] = self.format_time(nodeQ('div.info > div.shop-name').text())
#                 productInfo['img_url'] = nodeQ('div.pic > a > img').attr('src')
#                 productInfo.set_categories(category_info)
#                 productList.append(productInfo)
#             except Exception, e:
#                 print e 
#         return productList
#     
#     def format_time(self, text):
#         if not text:
#             return ""
#         fields = re.findall('[\d]{1,2}月[\d]{1,2}日', text)
#         return datetime.date(2016, int(fields[0]), int(fields[1])).strftime("%Y-%m-%d")
#     
#     def parseNextPageUrl(self, page_content):
#         if not re.findall('currentPage=([\d]+)&', self.current_url):
#             return 'http://www.vvic.com/list.html?currentPage=2&pageSize=50&pid=1&sort=up_time-desc#jump'
#         else:
#             pageNum = re.findall('currentPage=([\d]+)&', self.current_url)[0]
#             self.current_url = self.current_url.replace('currentPage=' + str(pageNum), 'currentPage=' + str(pageNum+1))
#             return self.current_url
#     
#     def needProductDetails(self):
#         return True
# 
#     def pasreProductDetails(self):
#         pass

#############################################################################################



