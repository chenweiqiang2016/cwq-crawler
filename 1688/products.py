# -*- coding: utf-8 -*-

# 2016/3/3 增加字段: tag star reviews total_sales
# 可能遭到屏蔽 只能适当时候运行
# TODO 解决错误: raise socket.error, msg  socket.error: [Errno 10060]

import httplib2
import uuid
import os
import re
import random
import time
import sys
import datetime
from pyquery import PyQuery
from utils import extractNum
from pics_1688 import get_img_urls

headers = ['level1_category', 'level2_category', 'level3_category',\
           'sku_id', 'product_name', 'product_price', 'product_url',\
           'img_url', 'img_urls', 'size', 'color', 'update_time', 'store_name',\
           'store_url', 'store_address', 'qq', 'telephone', 'supplier_name',\
           'city', 'reviews', 'tags', 'total_sales', 'monthly_sales']

class Product:
    def __init__(self):
        self.attrs = {}
        self.attrs['level1_category'] = "数码、电脑"
        self.attrs['level2_category'] = "3C数码配件"
        self.attrs['level3_category'] = "手机配件"
        
    def __getitem__(self, key):
        if self.attrs.has_key(key):
            return self.attrs[key]
        
    def __setitem__(self, key, value):
        self.attrs[key] = value;

def fetchContent(url, saveFile=False):
    sleep();
    h = httplib2.Http()
    response, content = h.request(url)
    #print response
    content = unicode(content, "GBK")
    if saveFile:
        filename = "C:/users/chenweiqiang/desktop/" + str(uuid.uuid4()) + '.html'
        fw = open(filename, 'w')
        fw.write(content.encode("utf-8")) #Q: unicode写不进去 utf-8可以正常写
        fw.close()
    return content

def sleep():
    times = random.uniform(2, 5)
    time.sleep(times)

def parsePage(content):
    doc = PyQuery(content)
    productNodeList = doc('div.mod-offer-list > ul.fd-clr > li')
    productList = []
    for node in productNodeList:
        nodeQ = PyQuery(node)
        p = Product();
        p['product_name'] = nodeQ('dd.description > a').text()
        p['product_price'] = nodeQ('dd.price > span.value').text()
        p['img_url'] = "http:" + nodeQ('dt.img-vertical > a > img').attr('data-lazyload-src')
        url = nodeQ('dt.img-vertical > a').attr('href')
        if url.find('http') == 0:
            p['product_url'] = url
        else:    
            p['product_url'] = "http:" + nodeQ('dt.img-vertical > a').attr('href')
        #print p['product_url']
        p['sku_id'] = re.findall('/(\d+)\.htm', p['product_url'])[0]
        #print p['sku_id']
        p['city'] = nodeQ('dd.origin > a').text()
        p['store_name'] =  nodeQ('dd.company').text()
        p['store_url'] = "http:" + nodeQ('dd.company > a').eq(-1).attr('href')
        #print p['store_url']
        p['monthly_sales']= nodeQ('dd.data > span.sold-out > em.num').text();
        #在产品列表页面增加一个字段
        p['tags'] = nodeQ("dd.signage > span").text()
        parseProductPage(p, True)
        parseStorePage(p)
        productList.append(p)
        #return productList #测试
    return productList

def parseProductPage(product, need_img_urls=False):
    """进入商品详情页, 抓取四个新字段
       delivery reviews star total_sales
    """
    if product['product_url']:
       content = fetchContent(product['product_url'], False)
       doc=PyQuery(content)
       #product['delivery'] = doc("div.cost-entries-type > p > em.value").text() 运费JS动态 解决不了
       product['reviews'] = doc('p.satisfaction-number > a > em.value').text()
       product['star'] = doc('p.star-level > i').attr("class")
       product['total_sales'] = doc('p.bargain-number > a > em.value').text()
       if need_img_urls:
           url_list = get_img_urls(content)
           product['img_urls'] = ', '.join(url_list)
       else:
           product['img_urls'] = ''
       product['color'], product['size'] = '', ''
       for index, td in enumerate(doc('div.obj-content > table > tbody > tr > td')):
            tdQ = PyQuery(td)
            if tdQ.attr('class') =='de-feature' and tdQ.text().strip() == u'颜色':
                product['color'] = PyQuery(doc('div.obj-content > table > tbody > tr > td')[index+1]).text()
            if tdQ.attr('class') =='de-feature' and tdQ.text().strip() == u'尺寸':
                product['size'] = PyQuery(doc('div.obj-content > table > tbody > tr > td')[index+1]).text()
       product['MOQ'] = extractNum(doc('tr.amount > td.ladder-1-1 > span.value').text().replace(u"≥", ""))
       if not product['MOQ'] or product['MOQ'] == 0:
           product['MOQ'] = extractNum(PyQuery(doc('tr.amount').remove('td.amount-title').children('td').eq(0))('span.value').text())
       if product['MOQ'] == 1:
           #print product['product_url']
           product['sku_size'] = PyQuery(doc('div.unit-detail-spec-operator').eq(0))('span.text').text()
           product['sku_color'] = PyQuery(doc('table.table-sku > tr').eq(0))('td.name').text()
           product['sku_price'] = PyQuery(doc('table.table-sku > tr').eq(0))('td.price').text()
           product['sku_amount'] = PyQuery(doc('table.table-sku > tr').eq(0))('td.count > span > em.value').text()
           print product['sku_id'], '\t', product['sku_size'], "\t", product['sku_color'], "\t", product['sku_price'], "\t", product['sku_amount']
    return product

store_info = {}

def parseStorePage(product):
    store_url = product['store_url']
#     index = store_url.find('1688.com')
#    store_url = store_url[:index]
    if store_url.endswith('/'):
        store_url = store_url[:-1]
    contact_url = store_url + '/page/contactinfo.htm'                           
    if store_info.has_key(contact_url):
        for key in store_info[contact_url].keys():
            product[key] = store_info[contact_url][key]
    else:
       content = fetchContent(contact_url)
       store_info[contact_url] = {}
       doc=PyQuery(content)
       product['supplier_name'] = doc('div.detail > div.contactSeller > span.disc').text()
       if not product['supplier_name']:
           product['supplier_name'] = doc('div.detail > div.contactSeller').remove('label').text()
       store_info[contact_url]['supplier_name'] = product['supplier_name']

       product['city'] = doc('div.detail > div.address > span.disc').text()
       if not product['city']:
           product['city'] = doc('div.detail').find('div.address').remove('label').text()
       store_info[contact_url]['city'] = product['city']

       product['mobile'], product['telephone'], product['store_address'] = '', '', ''
       for node in doc('div.contcat-desc > dl'):
           nodeQ = PyQuery(node)
           #print nodeQ.children('dt').text()
           if nodeQ.children('dt').text().strip() == u'电      话：':
               product['telephone'] = nodeQ.children('dd').text()
               store_info[contact_url]['telephone'] = product['telephone']
           if nodeQ.children('dt').text().strip() == u'地      址：':
               product['store_address'] = nodeQ.children('dd').text()
               store_info[contact_url]['store_address'] = product['store_address']
           if nodeQ.children('dt').text().strip() == u'移动电话：':
               product['mobile'] = nodeQ.children('dd').text()
               store_info[contact_url]['mobile'] = product['mobile']    
    return product

def persistance(objList, category):
    #fields = ['category', 'name', 'price', 'img_url', 'product_url', 'city', 'merchant', 'merchant_url', 'monthly_sales', 'tags', 'reviews', 'star', 'total_sales', 'img_urls']
    fields = ['level1_category', 'level2_category', 'level3_category',\
           'sku_id', 'product_name', 'product_price', 'product_url',\
           'img_url', 'img_urls', 'size', 'color', 'store_name',\
           'store_url', 'store_address', 'mobile', 'telephone', 'supplier_name',\
           'city', 'reviews', 'tags', 'monthly_sales', 'total_sales', 'MOQ']
    first_line = '\t'.join(fields) + '\n'
    fw = open(category + '_' + str(datetime.date.today()) + '_' + os.path.basename(__file__).split('.')[0] + "-result.csv", 'w')
    fw.write(first_line)
    for obj in objList:
        datas = []
        for key in fields:
            if (type(obj[key]) is unicode): #不加外围的括号产生bug
                obj[key] = obj[key].encode("utf-8")
            if (type(obj[key]) is int):
                obj[key] = str(obj[key])
            if not obj[key]: #NoneType
                obj[key] = ''
            datas.append(obj[key])
        line = '\t'.join(datas) + '\n'
        fw.write(line)
    fw.close()

def parseNextPageUrl(content):
    doc = PyQuery(content)
    if doc('div.page-bottom > a.page-next').attr('href'):
        return "http:" + doc('div.page-bottom > a.page-next').attr('href')

def main(start_url, limit):
    """完成各个方法的调度"""
    url = start_url
    LIMIT = limit #LIMIT = 5 #抓5个页面
    count = 1
    total_products = []
    while count <= LIMIT:
        content = fetchContent(url)
        mList = parsePage(content)
        total_products.extend(mList)
        url = parseNextPageUrl(content)
        count += 1
        if not url:
            break
    #以下三行的修改是为了其他代码的调用
    return total_products
    #persistance(total_merchants)
    #print "WELL DOME"

def set_categories(products, category):
    for p in products:
        p['category'] = category
        
def main_method_p(category, start_url):
    total_products = main(start_url, 14)
    #set_categories(total_products, category)
    persistance(total_products, category)
    print "WELL DOME"

if __name__ == '__main__':
    #category = sys.argv[1]
    #start_url = sys.argv[2]
    start_url = "https://ye.1688.com/chanpin/1046695-6970686f6e65b2caccf9.htm?spm=a360i.cyd0017.0.0.tVSI6s&homeType=2"
    #start_url="https://ye.1688.com/chanpin/-d4b0d2d5b9e0b8c8.htm?spm=a360i.cyd0017.0.0.XQ4lUU&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt"
    #start_url = "https://ye.1688.com/chanpin/-b3e8ceefd2c2b7fe.htm?spm=a360i.cyd0017.0.0.zk3ee8&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt"
    #start_url = "http://ye.1688.com/chanpin/-b4b0c1b1.htm?spm=a360i.cyd0017.0.0.Wl5YRp&homeType=1&analy=n&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt"
    main_method_p(u"iphone彩膜", start_url)