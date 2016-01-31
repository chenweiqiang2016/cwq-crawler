# -*- coding: utf-8 -*-


import json
import re
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
        product_info['raw_imgs'] = datas['data']['imgs'].strip()
        #处理一下
        aList = product_info['raw_imgs'].split(',')
        bList = []
        for item in aList:
            bList.append('http:' + item.strip())
        if product_info['img_url'] not in bList:
            bList.append(product_info['img_url'])
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