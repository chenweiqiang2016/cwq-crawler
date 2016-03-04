# -*- coding: utf-8 -*-

# 2016/3/3 增加字段: tag star reviews total_sales
# 可能遭到屏蔽 只能适当时候运行
# TODO 解决错误: raise socket.error, msg  socket.error: [Errno 10060]

import httplib2
import uuid
import os
import random
import time
from pyquery import PyQuery
from utils import extractNum

class Product:
    def __init__(self):
        self.attrs = {}
        self.attrs['category'] = "窗帘";
        
    def __getitem__(self, key):
        if self.attrs.has_key(key):
            return self.attrs[key]
        
    def __setitem__(self, key, value):
        self.attrs[key] = value;

def fetchContent(url, saveFile=False):
#     sleep();
    h = httplib2.Http()
    response, content = h.request(url)
    print response
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
        p['name'] = nodeQ('dd.description > a').text()
        p['price'] = nodeQ('dd.price > span.value').text()
        p['img_url'] = "http:" + nodeQ('dt.img-vertical > a > img').attr('data-lazyload-src')
        p['product_url'] = "http:" + nodeQ('dt.img-vertical > a').attr('href')
        p['city'] = nodeQ('dd.origin > a').text()
        p['merchant'] =  nodeQ('dd.company').text()
        p['merchant_url'] = "http:" + nodeQ('dd.company > a').eq(-1).attr('href')
        p['monthly_sales']= nodeQ('dd.data > span.sold-out > em.num').text();
        #在产品列表页面增加一个字段
        p['tags'] = nodeQ("dd.signage > span").text()
        parseProductPage(p)
        productList.append(p)
        #return productList #测试
    return productList

def parseProductPage(product):
    """进入商品详情页, 抓取四个新字段
       delivery reviews star total_sales
    """
    if product['product_url']:
       content = fetchContent(product['product_url'])
       doc=PyQuery(content)
       #product['delivery'] = doc("div.cost-entries-type > p > em.value").text() 运费JS动态 解决不了
       product['reviews'] = doc('p.satisfaction-number > a > em.value').text()
       product['star'] = doc('p.star-level > i').attr("class")
       product['total_sales'] = doc('p.bargain-number > a > em.value').text() 
    return product

def persistance(objList):
    fields = ['category', 'name', 'price', 'img_url', 'product_url', 'city', 'merchant', 'merchant_url', 'monthly_sales', 'tags', 'reviews', 'star', 'total_sales']
    first_line = '\t'.join(fields) + '\n'
    fw = open(os.path.basename(__file__).split('.')[0] + "-result.csv", 'w')
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

def main(start_url):
    """完成各个方法的调度"""
    url = start_url
    LIMIT = 5 #抓5个页面
    count = 1
    total_merchants = []
    while count <= LIMIT:
        content = fetchContent(url)
        mList = parsePage(content)
        total_merchants.extend(mList)
        url = parseNextPageUrl(content)
        count += 1
        if not url:
            break;
    persistance(total_merchants)
    print "WELL DOME"

if __name__ == '__main__':
    #start_url = "https://ye.1688.com/chanpin/-b3e8ceefd2c2b7fe.htm?spm=a360i.cyd0017.0.0.zk3ee8&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt"
    start_url = "http://ye.1688.com/chanpin/-b4b0c1b1.htm?spm=a360i.cyd0017.0.0.Wl5YRp&homeType=1&analy=n&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt"
    main(start_url)
    