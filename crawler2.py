# -*- coding: utf-8 -*-

import httplib2
import json
import sys
import datetime
import socket
import codecs
from utils import read_config, print_csvline, load_http_headers

class Merchant:
    def __init__(self, merchantName, url):
        self.merchantName = merchantName
        self.url = url
        self.productFields = ['level1_category', 'price',\
                              'img_url', 'name', 'sku_id',\
                              'product_url', 'store_name', \
                              'bname', 'update_time',\
                              'qq', 'telephone', 'marketName',\
                              'floor', 'position', 'supplier_name',\
                              'update_time', 'city', 'remark', 'imgs', 'size']
        self.crawlEntryUrl = None
        self.config = None

class CategoryInfo:
    def __init__(self, merchant):
        self.merchant = merchant
        self.parent_categories = None # a list
        
    def getLevel1Category(self):
        if not self.parent_categories:
            return self.name
        return self.parent_categories[0]
    
    def getLevel2Category(self):
        if self.parent_categories and len(self.parent_categories) >= 2:
            return self.parent_categories[1]
        elif self.parent_categories and len(self.parent_categories) == 1:
            return self.name
        return None

    def getLevel3Category(self):
        if self.parent_categories and len(self.parent_categories) == 2:
            return self.name
  
class ProductInfo():
    def __init__(self, merchant):
        self.merchant = merchant
        self.attrs = {}
    
    def __getitem__(self, key):
        if self.attrs.has_key(key):
            return self.attrs.get(key)
    
    def __setitem__(self, key, value):
        self.attrs[key] = value

    def set_categories(self, category_info):
        if category_info.getLevel1Category():
            self['level1_category'] = category_info.getLevel1Category()
        if category_info.getLevel2Category():
            self['level2_category'] = category_info.getLevel2Category()
        if category_info.getLevel3Category():
            self['level3_category'] = category_info.getLevel3Category()
    
    def to_list(self):
        result = []
        for field in self.merchant.productFields:
            result.append(self[field])
        return result

class FetchTask:
    def __init__(self, **kwargs):
        self.url = kwargs['url']
        self.headers = kwargs['headers']
        self.encoding = kwargs['encoding']
    
    def to_str(self):
        dic_json = {'url': self.url,
                    'headers': self.headers,
                    'encoding': self.encoding}
        return json.dumps(dic_json)

class Fetcher:
    def __init__(self, merchant):
        self.merchant = merchant
        
    def fetch(self, task):
        h = httplib2.Http(timeout=30)
        response, content = h.request(uri=task.url,
                                      method='GET',
                                      headers=task.headers)
        return response.status, content
    
    def getHtmlDoc(self, fetchTask, try_times):
        status, content = 200, ''
        times = 0
        while True:
            times += 1
            try:
                status, content = self.fetch(fetchTask)
                if status in [200]:
                    break
            except httplib2.ServerNotFoundError, e:
                print e
            except socket.error, e:
                print e
            except httplib2.RelativeURIError, e:
                print e
            if times >= try_times:
                break
        return status, content
    
    def fetchCategoryPageContent(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8', 
                              headers=self.merchant.headers)
        status, content = self.getHtmlDoc(fetchTask, 5)
        return content
    
    def fetchProductListPageContent(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8',
                              headers={})
        status, content = self.getHtmlDoc(fetchTask, 3)
        return content

    def fetchProductPageContent(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8',
                              headers={})
        status, content = self.getHtmlDoc(fetchTask, 3)
        return content
    
    def fetchPageWithoutHeaders(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8',
                              headers={})
        status, content = self.getHtmlDoc(fetchTask, 3)
        return content

class Crawler:
    def __init__(self, merchant, parser):
        self.merchant = merchant
        self.fetcher = Fetcher(merchant)
        self.parser = parser
        self.filename = merchant.merchantName + '_' + datetime.date.today().strftime("%m-%d-%Y") + '_productInfo.inprogress'
        self.fw = open(self.filename, 'w')
        self.fw.write(codecs.BOM_UTF8)
        self.fw.write('\t'.join(self.merchant.productFields) + '\n')
        #换一种写法
#         first_line = self.merchant.productFields[0]
#         for index in range(1, len(self.merchant.productFields)):
#             first_line += ('\t' + self.merchant.productFields[index]) 
#         print_csvline(self.fw, first_line)

    def crawl(self):
        categoryList = self.getInitialCategories()
        self.crawlCategoryList(categoryList)
        self.fw.close()

    def getInitialCategories(self):
        homepage_content =self.fetcher.fetchCategoryPageContent(self.merchant.crawlEntryUrl)
        categoryList = self.parser.parseCategories(homepage_content)
        return categoryList
    
    def crawlCategoryList(self, categoryList):
        for category in categoryList:
            self.crawlProducts(category)
        
    def crawlProducts(self, category_info):
        url = category_info.url
        page_num = 0
        while True:
            products_page_content = self.fetcher.fetchProductListPageContent(url)
            parsed_products = self.parser.parseProductsByCategory(products_page_content, category_info)
            page_num += 1
            for productInfo in parsed_products:
                try:
                    if self.parser.needProductDetails():
                        #所属店铺的一些信息
                        #http://www.vvic.com/api/shop/13906
                        shop_api_content = self.fetcher.fetchProductPageContent("http://www.vvic.com/api/shop/" + productInfo['shop_id'])
                        self.parser.parseShopDetails(shop_api_content, productInfo)
                        #多个图片的url
                        #http://www.vvic.com/api/item/700188
                        item_api_content = self.fetcher.fetchProductPageContent("http://www.vvic.com/api/item/" + productInfo['sku_id'])
                        self.parser.parseItemDetails(item_api_content, productInfo)
                    print_csvline(self.fw, productInfo.to_list())
                except Exception, e:
                    print e
                    print 'url:', productInfo['product_url']
            if page_num >= 60:
                break
            url = self.parser.parseNextPageUrl(products_page_content)
            if not url:
                break

class Parser:
    def __init__(self, merchant):
        self.merchant = merchant

    def parseCategories(self, homepage_content):
        pass
    
    def parseNextPageUrl(self, products_page_content):
        pass
    
    def newCategory(self):
        return CategoryInfo(self.merchant)
    
    def newProduct(self):
        return ProductInfo(self.merchant)
    

def init_merchant(merchantName):
    configFile = './config/' + merchantName + '.cfg'
    config = read_config(configFile)
    siteUrl = config.get2("url")
    if not siteUrl:
        siteUrl = 'www.' + merchantName + '.com'
    m = Merchant(merchantName, siteUrl)
    m.crawlEntryUrl = config.get2("crawlEntryUrl")
    headersFile = config.get2("headersFile")
    if headersFile:
        m.headers = load_http_headers('./config/' + headersFile)
    m.config = config
    return m

def crawl(merchantName):
    merchant = init_merchant(merchantName)
    moduleName, parserClassName = merchant.config.get2('parser').split(".")
    module = __import__(moduleName)
    parserClass = getattr(module, parserClassName)
    parser = parserClass(merchant)
    crawler = Crawler(merchant, parser)
    crawler.crawl()
    print 'Well done.'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, 'Usage: python crawler2.py <merchantName>'
        sys.exit(1)
    merchantName = sys.argv[1]
    crawl(merchantName)
    print 'End.'

    
        
