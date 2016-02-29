# -*- coding: utf-8 -*-

import httplib2
import uuid
import os
from pyquery import PyQuery
from utils import extractNum

class Merchant:
    def __init__(self):
        self.attrs = {}
        self.attrs['category'] = "宠物衣服";
        
    def __getitem__(self, key):
        if self.attrs.has_key(key):
            return self.attrs[key]
        
    def __setitem__(self, key, value):
        self.attrs[key] = value;

def fetchContent(url, saveFile=False):
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
    merchantNodeList = doc('div.mod-company-list > div.item')
    merchantList = []
    for node in merchantNodeList:
        nodeQ = PyQuery(node)
        m = Merchant();
        m['city'] = nodeQ('div.origin').find('div.container > a').text()
        m['name'] = nodeQ("dl[class='info basic-info'] > dt > a").eq(-1).text()
        m['url'] = "http:" + nodeQ("dl[class='info basic-info'] > dt > a").eq(-1).attr('href')
        m['main_products'] = PyQuery(nodeQ("dl[class='info basic-info'] > dd").eq(1)).children("span.value").text()
        m['address'] = PyQuery(nodeQ("dl[class='info basic-info'] > dd").eq(2)).children("span.value").text()
        m['satisfaction_rate'] = nodeQ("dl[class='info basic-info'] > dd.probability > span > em.value").eq(0).text()
        m['retention_rates'] = nodeQ("dl[class='info basic-info'] > dd.probability > span > em.value").eq(1).text()
        m['weekly_sales'] = extractNum(nodeQ('dd > span.num').text())
        merchantList.append(m)
    return merchantList

def persistance(objList):
    fields = ['category', 'city', 'name', 'url', 'main_products', 'address', 'satisfaction_rate', 'retention_rates', 'weekly_sales']
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
    start_url = "https://ye.1688.com/qiye/-b3e8ceefd2c2b7fe.htm?spm=a360i.cyd0018.0.0.Tm8FDX&homeType=1&sortType=SALE_QUANTITY#filt"
    main(start_url)
    