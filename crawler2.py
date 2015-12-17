# -*- coding: utf-8 -*-

import httplib2
import json
import sys
import datetime
import socket
import lockfile
import os
import re
import shutil
import time
import random
import ConfigParser
import StringIO
import codecs
import logging
from logging import debug, info, warning, error
from utils import read_config, print_csvline, load_http_headers, read_headers
import stat_data

class Merchant:
    def __init__(self, merchantName, url, crawlEntryUrl=None):
        self.merchantName = merchantName
        self.wwwDomain = url
        self.homeUrl = "http://" + url
        self.headers = {}
        self.crawlEntryUrl = crawlEntryUrl if crawlEntryUrl else self.homeUrl
        self.sleepSeconds = 2, 5
        self.productFields = ['level1_category', 'level2_category', 'level3_category',\
                               'name', 'product_url', 'img_url',\
                               'sku_id', 'price', 'reviews']
        self.maxPagesPerCategory = 999
        self.includedCategories = ''
        self.excludedCategories = ''
        self.useDistributedFetch = False
        self.useWebClient = False
        self.isSavePages = False
        self.config = None
    
    def initStoreDir(self):
        rel_path = self.config.get2('savePagesDir')
        if not rel_path:
            error("No store dir configured to store pages... EXIT!")
            raise Exception("No store dir configured to store pages... EXIT!")
        abs_path = os.path.join(os.getcwd(), os.path.join(rel_path, self.merchantName))
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
    
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
    
    def isCategoryIncluded(self, level1Name, level2Name):
        if not self.includedCategories:
            return True
        fp = StringIO.StringIO(self.includedCategories)
        for line in fp:
            fields = line.strip().split('/')
            if fields[0].strip() == level1Name:
                if fields[1].strip() == level2Name or fields[1].strip().upper == 'ALL':
                    return True
        return False

    def isCategoryExcluded(self, level1Name, level2Name):
        if not self.excludedCategories:
            return False
        fp = StringIO.StringIO(self.excludedCategories)
        for line in fp:
            fields = line.strip().split('/')
            if fields[0].strip() == level1Name:
                if fields[1].strip() == level2Name or fields[1].strip().upper == 'ALL':
                    return True
        return False

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
    
    def formalize(self):
        self.url = self.merchant.filteruri(self.url)
        return self
    
    def __str__(self):
        cate_str = self.getLevel1Category()
        if self.getLevel2Category():
            cate_str += (' > ' + self.getLevel2Category())
            if self.getLevel3Category():
                cate_str += (' > ' + self.getLevel3Category())
        return cate_str
  
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
            result.append(self.item_encode(self[field]))
        return result
    
    def item_encode(self, item):
        if not item: #''
            return ''
        elif isinstance(item, unicode):
            return item.encode('utf-8')
        else:
            return str(item)
    
    def formalize(self):
        self['name'] = self.formalize_name()
        return self
    
    def formalize_name(self):
        #name存在换行
        #http://www.houzz.com/photos/40672073/Negin-Sofa-Bed-Turquoise-Fabric-Espresso-Rattan-modern-futons
        return re.sub('\s+', ' ', self['name'].strip())

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
    
    def sleep(self):
        time.sleep(random.uniform(2, 5))
        
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
            self.sleep()
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

class RabbitmqFetcher(Fetcher):
    pass

class Crawler:
    def __init__(self, merchant, parser):
        self.merchant = merchant
        self.parser = parser
        self.config = read_config('config/crawl.cfg')
        if self.merchant.useDistributedFetch and self.config.get2('rabbitmq.server', section=''):
            self.fetcher = RabbitmqFetcher()
        else:
            self.fetcher = Fetcher(merchant)
        filename = '%s_%s_productInfo.inprogress' %(merchant.merchantName, datetime.date.today().strftime("%m-%d-%Y"))
        self.filename = os.path.join(self.config.get('all', 'save.dir'), filename)
        self.fp = None
        self.cachedProducts = {}
    
    def rmCleanFile(self):
        if os.path.exists(self.filename):
            fp = open(self.filename, 'r')
            line = fp.readline().strip()
            if not line:
                os.remove(self.filename)
            fp.close()

    def initDataFile(self):
        crawledProducts = []
        if os.path.exists(self.filename):
            info("open origin file to analyse.")
            self.fp = open(self.filename, 'r')
            line = self.fp.readline()
            headers = read_headers(line)
            if headers == self.merchant.productFields:
                url_idx = headers.index('product_url')
                info("loading datas from origin file...")
                for line in self.fp.readlines():
                    data = line.strip().split('\t')
                    if len(data) != len(headers):
                        continue
                    crawledProducts.append(data)
                    self.cachedProducts[data[url_idx]] = 1
            info("find %s count of products." %(len(crawledProducts)))
            self.fp.close()
        #将headers以及已经抓取的商品信息写入文件
        self.fp = open(self.filename, 'w')
        self.fp.write(codecs.BOM_UTF8)
        self.fp.write('\t'.join(self.merchant.productFields) + '\n')
        for product in crawledProducts:
            print_csvline(self.fp, product)

    def crawl(self):
        #删除空文件
        self.rmCleanFile()
        #初始化文件, 复用已经抓取的数据
        self.initDataFile()
        #从入口页获取可以获得的全部品类
        categoryList = self.getInitialCategories()
        if not categoryList:
            raise Exception("Crawl Entrance Page Failed. Please Improve Program.")
        #根据url进行一次去重
        categoryList = self.rmDuplicateCategories(categoryList)
        info("From the entrance page, we get following categories, totally %s:" %len(categoryList))
        for category in categoryList:
            info(category)
        info("Verify whether the category is configured to crawl...")
        categoryList = [category for category in categoryList if self.merchant.isCategoryIncluded(category.getLevel1Category(),
                                                                                                  category.getLevel2Category())]
        categoryList = [category for category in categoryList if not self.merchant.isCategoryExcluded(category.getLevel1Category(),
                                                                                                      category.getLevel2Category())]
        info("After reduce according to config file, %d category left." %len(categoryList))
        if not categoryList:
            raise Exception("No Categories Configured To Crawl. Please Check!")
        else:
            info('After verification, we need to crawl below categories, totally %d: ' %(len(categoryList)))
            for category in categoryList:
                info(category)
        try:
            self.crawlCategoryList(categoryList)
        except Exception, e:
            print e
        finally:
            self.fp.close()
        
        self.renameAndGeneExcel()
        
        self.statScoringField()
        
        info('crawl end.')


    def getInitialCategories(self):
        homepage_content =self.fetchCategoryPageContent(self.merchant.crawlEntryUrl)
        categoryList = self.parser.parseCategories(homepage_content)
        return categoryList
    
    def rmDuplicateCategories(self, categoryList):
        newList = []
        urls = {}
        for category in categoryList:
            if not urls.has_key(category.url):
                newList.append(category)
                urls[category.url] = category
        return newList
    
    def crawlCategoryList(self, categoryList):
        for index, category in enumerate(categoryList):
            info('crawling category(%s of %s): %s @ %s' %((index+1), len(categoryList), category, category.url))
            self.crawlProducts(category)
        
    def crawlProducts(self, category_info):
        url = category_info.url
        category_idx, page_idx = 0, 0
        success_count, fail_count, total_count = 0, 0, 0
        while True:
            num_idx = 0
            products_page_content = self.fetchProductListPageContent(url)
            page_idx += 1
            parsed_products = self.parser.parseProductsByCategory(products_page_content, category_info)
            for productInfo in parsed_products:
                num_idx += 1
                category_idx += 1
                if self.cachedProducts.has_key(productInfo['product_url']):
                    continue
                try:
                    if self.parser.needProductDetails():
                        product_page_content = self.fetcher.fetchProductPageContent(productInfo['product_url'])
                        self.parser.parseProductDetails(product_page_content, productInfo)
                    if self.parser.needRankInfo():
                        productInfo['page_idx'] = str(page_idx)
                        productInfo['num_idx'] = str(num_idx)
                        productInfo['category_index'] = str(category_idx)
                    print_csvline(self.fp, productInfo.formalize().to_list())
                    success_count += 1
                except:
                    fail_count += 1
                finally:
                    total_count += 1
                    if(total_count % 100 == 0):
                        info("Below current category, crawled products: %s (%s success, %s failed)" %(total_count, success_count, fail_count))
            url = self.parser.parseNextPageUrl(products_page_content) if len(parsed_products) > 4 else None
            if not url:
                break
            if page_idx >= self.merchant.maxPagesPerCategory: #等于10表示第十页抓完
                break
        info("category: %s, totally crawled products: %s (%s success, %s failed)" %(category_info, total_count, success_count, fail_count))

    def fetchCategoryPageContent(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8', 
                              headers=self.merchant.headers)
        info("fetching category page @ %s" %furl)
        status, content = self.fetcher.getHtmlDoc(fetchTask, 5)
        return content
    
    def fetchProductListPageContent(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8',
                              headers={})
        info("fetching productList page @ %s" %furl)
        status, content = self.fetcher.getHtmlDoc(fetchTask, 3)
        return content

    def fetchProductPageContent(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8',
                              headers={})
        info("fetching product page @ %s" %furl)
        status, content = self.fetcher.getHtmlDoc(fetchTask, 3)
        return content
    
    def fetchPageWithoutHeaders(self, furl):
        fetchTask = FetchTask(url=furl,
                              encoding='utf-8',
                              headers={})
        info("fetching page without headers @ %s" %furl)
        status, content = self.fetcher.getHtmlDoc(fetchTask, 3)
        return content
    
    def fetchSocialLikes(self, url):
        furl = 'http://graph.facebook.com/' + url
        debug('fetching facebook likes of product @ %s', url)
        content = self.fetchPageWithoutHeaders(furl)
        datas = json.loads(content)
        if datas.has_key('shares'):
            return datas['shares']
    
    def renameAndGeneExcel(self):
        finalFilename = self.filename.replace("inprogress", "csv")
        os.rename(self.filename, finalFilename)
        self.filename = finalFilename

    def statScoringField(self):
        stat = stat_data.Stat(self.filename)
        statResult = stat.stat()
        dist = statResult.output()
        info("stat:\n%s" %dist)

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

LEVELS = {
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR
          }    

def logging_params(merchantName, config):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    logFilename = './logs/' + merchantName + '.log'
    if config.get2('logLevel'):
        logLevel = LEVELS[config.get2('logLevel')]
    else:
        logLevel = logging.INFO
    return logFilename, logLevel
    
def config_log(merchantName, config):
    logFilename, logLevel = logging_params(merchantName, config)
    logging.basicConfig(filename=logFilename,
                        level=logLevel,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%a %Y/%m/%d %H:%M:%S",
                        filemode="w")

def init_merchant(merchantName, config):
    siteUrl = config.get2("url")
    #避免config未填写url配置信息报错
    if not siteUrl:
        siteUrl = 'www.' + merchantName + '.com'
    m = Merchant(merchantName, siteUrl)
    m.crawlEntryUrl = config.get2("crawlEntryUrl")
    m.productFields = config.getList("productFields")
    m.sleepSeconds = tuple(item for item in config.getList('sleepSeconds'))
    headersFile = config.get2("headersFile")
    if headersFile:
        m.headers = load_http_headers('./config/' + headersFile)
    if config.get2('maxPagesPerCategory'):
        m.maxPagesPerCategory = int(config.get2('maxPagesPerCategory'))
    m.useWebClient = config.getBoolean('useWebClient')
    m.includedCategories = config.get2('includedCategories', multiLines=True)
    m.excludedCategories = config.get2('excludedCategories', multiLines=True)
    m.config = config
    if config.getBoolean('isSavePages'):
        m.initStoreDir()
    return m

def crawl(merchantName, config):
    merchant = init_merchant(merchantName, config)
    info("init parser...")
    moduleName, parserClassName = merchant.config.get2('parser').split(".")
    module = __import__(moduleName)
    parserClass = getattr(module, parserClassName)
    parser = parserClass(merchant)
    info("init crawler...")
    crawler = Crawler(merchant, parser)
    parser.crawler = crawler  #方便调用一些方法
    crawler.crawl()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, 'Usage: python crawler2.py <merchantName>'
        sys.exit(1)
    merchantName = sys.argv[1]
    #应该将设置log提前
    configFile = './config/' + merchantName + '.cfg'
    config = read_config(configFile)
    config_log(merchantName, config)
    try:
        checkLock = False #生产环境应该明确为True
        lock = lockfile.FileLock("crawl-" + merchantName)
        info("Try to acquire a lock of merchant <%s>..." %merchantName)
        try:
            lock.acquire(10)
            info("Well done, we generate a new lock.")
        except Exception, e:#Timeout waiting to acquire lock for
                warning("A lock with same name exists, we just use it as new lock or stop our work?")
                if checkLock:
                    warning("Yes, we just stop the work.")
                    sys.exit(1)
                else:
                    info("No, we just use the old one and go on running.")
        crawl(merchantName, config)
    except Exception, e:
        print e
    finally:
        try:
            if locals().has_key('lock'): #'var'
                lock.release() #lockfile.NotMyLock: crawl-xxx is locked, but not by me
                info('New lock release!')
        except lockfile.NotMyLock, e:
            if not checkLock: #除非明确要求, 否则我们不该随便删除已经存在的锁
                shutil.rmtree('crawl-' + merchantName + '.lock', True)
                info('After work, we remove the old lock with same name!')
        info("\n\n")
