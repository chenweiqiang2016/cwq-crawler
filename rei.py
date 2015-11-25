# -*- coding: utf-8 -*-

# 2015/10/31 抓取一级品类下的全部二级品类     商品入口: 二级品类

from crawler2 import Parser
from pyquery import PyQuery
import re
import json

class ReiParser(Parser):

    current_url = None
    current_category = None

    def parseCategories(self, homepage_content):
        categoryList = []
        doc = PyQuery(homepage_content)
        #只获取第一个一级品类的展开 Camp & Hike
        node = doc('div[class="mega-menu-container container js-mega-menus-target"] > div > div > section').eq(0)
        nodeList = PyQuery(node).find("div.row > div.col-xs-2 > a") #a > h4是品类名  Accessories没有<a>忽略
        for node in nodeList:
            nodeQ = PyQuery(node)
            categoryInfo = self.newCategory()
            categoryInfo.name = nodeQ.text()
            categoryInfo.url = nodeQ.attr('href')
            self.process_url(categoryInfo)
            if categoryInfo.name and categoryInfo.url:
                categoryInfo.parent_categories = ['Camp & Hike']
                categoryList.append(categoryInfo.formalize())
        return categoryList
    
#     def process_url(self, categoryInfo):
#         if re.findall('/[\w]+/([\w-]+)$', categoryInfo.url):
#             #这种根据实际url的方法抓不着
#             #categoryInfo.url = categoryInfo.url + '?r=c&ir=category%3A'+ re.findall('/[\w]+/([\w-]+)$', categoryInfo.url)[0] + '&page=1'
#             #抓json数据
#             categoryInfo.url = 'http://www.rei.com/rest/search/results?ir=category%3A' + re.findall('/[\w]+/([\w-]+)$', categoryInfo.url)[0] + '&page=1&pagesize=30'
    
    def process_url(self, categoryInfo):
        if categoryInfo.name == "Backpacks":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Ahiking-backpacks&sx=r10%2FhloVVkDGKWhCxODMMQ%3D%3D&ir=category%3Ahiking-backpacks&pagesize=30"
        elif categoryInfo.name == "Tents":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Atents&sx=aao8XOmlfpLm7nm6K%2BnzPw%3D%3D&ir=category%3Atents&pagesize=30"
        elif categoryInfo.name == "Sleeping Bags":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Asleeping-bags-and-accessories&sx=tnTNLIKQjiSpbzhEVkiMeQ%3D%3D&ir=category%3Asleeping-bags-and-accessories&pagesize=30"
        elif categoryInfo.name == "Pads & Hammocks":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Asleeping-pads-cots-and-hammocks&sx=lMWXY9xqI%2BtTdvau0yowKA%3D%3D&ir=category%3Asleeping-pads-cots-and-hammocks&pagesize=30"
        elif categoryInfo.name == "Camp Kitchen":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Acamp-kitchen&sx=oVDesyK0Mrg%2BhAqaiSsRHA%3D%3D&ir=category%3Acamp-kitchen&pagesize=30"
        elif categoryInfo.name == "Camp Furniture":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Acamp-furniture&sx=%2Fq6Mgp6Z5Z6hTmOvHHCHeg%3D%3D&ir=category%3Acamp-furniture&pagesize=30"
        elif categoryInfo.name == "Water":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Awater-bottles-and-treatment&sx=BShiBDxnIOi50NdDoZvObg%3D%3D&ir=category%3Awater-bottles-and-treatment&pagesize=30"
        elif categoryInfo.name == "Lighting":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Acamp-lighting&sx=TQEEN99aJrDAcZiOh6heOw%3D%3D&ir=category%3Acamp-lighting&pagesize=30"
        elif categoryInfo.name == "Electronics":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Acamp-electronics&sx=OFLEyOCl1rwRFWmNbA7JPg%3D%3D&ir=category%3Acamp-electronics&pagesize=30"
        elif categoryInfo.name == "Gadgets & Gear":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Agadgets&sx=glTdDBkw0Q8VoQyIgVbx2g%3D%3D&ir=category%3Agadgets&pagesize=30"
        elif categoryInfo.name == "Hiking Footwear":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Ahiking-footwear&sx=fEoen0b3yd%2Bt2ioQa3dv9g%3D%3D&ir=category%3Ahiking-footwear&pagesize=30"
        elif categoryInfo.name == "Hiking Clothing":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Ahiking-clothing&sx=fQzIoCDT9BYcJmcCQZx7Dw%3D%3D&ir=category%3Ahiking-clothing&pagesize=30"
        elif categoryInfo.name == "Health & Safety":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&r=category%3Ahealth-and-safety&sx=2G%2BG780nF3CzYMiMFcyjGA%3D%3D&ir=category%3Ahealth-and-safety&pagesize=30"
        elif categoryInfo.name == "Camp & Hike Deals":
            categoryInfo.url = "http://www.rei.com/rest/search/results?page=1&sx=GKc2Dxh5Q%2Fu2AHCfm5JY1w%3D%3D&ir=collection%3Acamping-and-hiking-deals&collection=camping-and-hiking-deals&pagesize=30"
        
    def parseProductsByCategory(self, category_page_content, category_info):
        #http://www.rei.com/c/hiking-backpacks?r=c&ir=category%3Ahiking-backpacks&page=1
        #productNodeList = doc('div#result-container > div')
        if self.current_category == None or self.current_category.url != category_info.url:
            self.current_category = category_info
            self.current_url = category_info.url

        json_datas = json.loads(category_page_content)
        productList = []
        for productItem in json_datas['results']:
            productInfo = self.newProduct()
            productInfo['name'] = productItem['cleanTitle']
            productInfo['product_url'] = self.merchant.filteruri(productItem['link'])
            productInfo['sku_id'] = productItem['prodId']
            productInfo['reviews'] = productItem['reviewCount']
            productInfo['img_url'] = 'http://www.rei.com/zoom/' + productInfo['sku_id'] + '/230'#230是像素
            productInfo['label_price'] = str(productItem['displayPrice']['compareAt'])
            if productItem['displayPrice']['priceDisplay']['salePrice']:
                productInfo['price'] = str(productItem['displayPrice']['priceDisplay']['salePrice'])
            else:
                productInfo['price'] = productInfo['label_price']
#             #下面这种方式也是可以的 只是使用了上面的方法更简单
#             productInfo['label_price'] = productItem['regularPrice']
#             if re.findall('[1-9]', productItem['percentageOff']): #有这种情况.00
#                 productInfo['price'] = (1-float(productItem['percentageOff'])/100.0) * float(productItem['regularPrice'])
#             else:
#                 productInfo['price'] = productItem['regularPrice']
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList

    def parseNextPageUrl(self, category_page_content):
        pageNum = int(re.findall('page=([\d]+)&', self.current_url)[0])
        if pageNum >=10:
            return None
        else:
            self.current_url = self.current_url.replace('page='+str(pageNum), 'page='+str(pageNum+1))
            return self.current_url
        
