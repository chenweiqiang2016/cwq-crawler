# -*- coding: utf-8 -*-

import httplib2
import uuid
import os
from pyquery import PyQuery
from utils import extractNum

class Product:
    def __init__(self):
        self.attrs = {}
        self.attrs['category'] = "宠物衣服";
        
    def __getitem__(self, key):
        if self.attrs.has_key(key):
            return self.attrs[key]
        
    def __setitem__(self, key, value):
        self.attrs[key] = value;

def fetchContent(url, saveFile=True):
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
        productList.append(p)
    return productList

def persistance(objList):
    fields = ['category', 'name', 'price', 'img_url', 'product_url', 'city', 'merchant', 'merchant_url', 'monthly_sales']
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
    start_url = "https://ye.1688.com/chanpin/-b3e8ceefd2c2b7fe.htm?spm=a360i.cyd0017.0.0.zk3ee8&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt"
    main(start_url)
    