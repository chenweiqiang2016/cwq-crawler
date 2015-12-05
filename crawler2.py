# -*- coding: utf-8 -*-

import httplib2
import json
import sys
import datetime
import socket
import lockfile
import os
import shutil
import logging
from logging import debug, info, warning, error
from utils import read_config, print_csvline, load_http_headers


class Merchant:
    def __init__(self, merchantName, url):
        self.merchantName = merchantName
        self.wwwDomain = url
        self.homeUrl = "http://" + url
        self.productFields = ['level1_category', 'level2_category', 'level3_category',\
                               'name', 'product_url', 'img_url',\
                               'sku_id', 'price', 'reviews']
        self.crawlEntryUrl = None
        self.config = None
    
    def filteruri(self, uri):
        if uri.startswith("http"):
            return uri
        elif uri.startswith("//"):
            return 'http' + uri
        else:
            if not self.homeUrl.endswith('/'):
                homeUrl = self.homeUrl + '/'
            if uri.startswith('/'):
                uri = uri[1:]
            return homeUrl + uri

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
    
    def fetchSocialLikes(self, url):
        furl = 'http://graph.facebook.com/' + url
        content = self.fetchPageWithoutHeaders(furl)
        datas = json.loads(content)
        if datas.has_key('shares'):
            return datas['shares']

class Crawler:
    def __init__(self, merchant, parser):
        self.merchant = merchant
        self.fetcher = Fetcher(merchant)
        self.parser = parser
        self.filename = merchant.merchantName + '_' + datetime.date.today().strftime("%m-%d-%Y") + '_productInfo.inprogress'
        self.fw = open(self.filename, 'w')

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
        category_idx, page_idx = 0, 0
        while True:
            num_idx = 0
            products_page_content = self.fetcher.fetchProductListPageContent(url)
            page_idx += 1
            parsed_products = self.parser.parseProductsByCategory(products_page_content, category_info)
            for productInfo in parsed_products:
                num_idx += 1
                category_idx += 1
                if self.parser.needProductDetails():
                    product_page_content = self.fetcher.fetchProductPageContent(productInfo['product_url'])
                    self.parser.parseProductDetails(product_page_content, productInfo)
                if self.parser.needRankInfo():
                    productInfo['page_idx'] = str(page_idx)
                    productInfo['num_idx'] = str(num_idx)
                    productInfo['category_index'] = str(category_idx)
                print_csvline(self.fw, productInfo.to_list())
            url = self.parser.parseNextPageUrl(products_page_content)
            if not url:
                break

class Parser:
    def __init__(self, merchant):
        self.merchant = merchant
        self.crawler = None

    def parseCategories(self, homepage_content):
        pass
    
    def parseNextPageUrl(self, products_page_content):
        pass
    
    def needProductDetails(self):
        return False
    
    def needRankInfo(self): #现阶段都是需要的
        return True
    
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
    m.productFields = config.getList("productFields")
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
    parser.crawler = crawler  #方便调用一些方法
    crawler.crawl()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, 'Usage: python crawler2.py <merchantName>'
        sys.exit(1)
    merchantName = sys.argv[1]
    #1. 一次完整的运行总是会运行crawl()方法, 并将锁解除
    #2. 文件目录下无锁时, 生成新锁, 最后release()
    #3. 文件目录下有锁时, 使用就锁, 最后remove()
    try:
        isLockCrawlMerchant = True
        if isLockCrawlMerchant:
            lock = lockfile.FileLock("crawl-" + merchantName)
            info("Try to acquire a lock of merchant <%s>..." %merchantName)
            try:
                lock.acquire(10)
                info("Well done, we generate a new lock.")
            except Exception, e:
                warning("A lock with same name exists, we just use it as new lock or stop our work?")
                debug(e)  #Timeout waiting to acquire lock for
        else:
            info("Maybe we are testing, without using lock...")
        crawl(merchantName)
    except Exception, e:
        print e
    finally:
        try:
            if locals().has_key('lock'): #'var'
                lock.release() #lockfile.NotMyLock: crawl-xxx is locked, but not by me
                info('New lock release!')
        except lockfile.NotMyLock, e:
            shutil.rmtree('crawl-' + merchantName + '.lock', True)
            info('After work, we remove the old lock with same name!')

