# -*- coding: utf-8 -*-

import sys
import random
import time
import httplib2
import uuid
from pyquery import PyQuery

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
    
def pase_stock_case(url):
    content = fetchContent(url, True)
    doc=PyQuery(content)
    sku_size = PyQuery(doc('div.unit-detail-spec-operator').eq(0))('span.text').text()
    sku_color = PyQuery(doc('table.table-sku > tr').eq(0))('td.name').text()
    sku_price = PyQuery(doc('table.table-sku > tr').eq(0))('td.price').text()
    sku_amount = PyQuery(doc('table.table-sku > tr').eq(0))('td.count > span > em.value').text()
    print sku_size, sku_color, sku_price, sku_amount
    
if __name__ == '__main__':
    url = sys.argv[1]
    pase_stock_case(url)