# -*- coding: utf-8 -*-
'''
Created on 2015年11月2日

@author: Chen Weiqiang

直接抓取爆款易页面满足特定条件(周销量大于10)的商品

手动抓取11个页面
'''

from pyquery import PyQuery
import httplib2
import re


def parseProducts(category_page_content):
    doc = PyQuery(category_page_content)
    productList = []
    nodeList = doc('div#categoryHotProductTable > table.responstable > tbody > tr')
    for node in nodeList:
        product = []
        nodeQ = PyQuery(node)
        tdList = nodeQ.children('td')
        product.append(PyQuery(tdList[0]).children('img').attr('ng-src'))
        product.append(PyQuery(tdList[1]).children('a').attr('href'))
        product.append(PyQuery(tdList[1]).children('a').text())
        product.append(PyQuery(tdList[2]).text())
        product.append(PyQuery(tdList[4]).text())
        product.append(PyQuery(tdList[8]).text())
        product.append(re.findall('/([\d]+)$', product[1])[0]) #不加任何检查
        productList.append(product)
    return productList

def fetchPageContent(furl, form, count):
    if form == 'manual':
        pages = 11
        if count < pages:
            fr = open('C:/users/administrator/desktop/' + str(count+1) + '.html', 'r')
            content = fr.read()
            fr.close()
            return content
    else:
        h = httplib2.Http()
        response, content = h.request(uri=furl, method='GET', headers={})
        if response.status == 200:
            return content

def record(productList):
    fw = open('results.csv', 'w')
    fw.write('img_url\tproduct_url\tname\treviews\tprice\tstore_name\tsku_id\n')
    for product in productList:
        line = '\t'.join(product)
        fw.write(line + '\n')
    fw.close()

if __name__ == '__main__':
    totalProducts = []
    count = 0
    while True:
        if count > 10:
            break
        content = fetchPageContent('http://www.baokuanyi.com/product/analysis/detail/item?q=-0&platform=ebay&type=category&keyword=plus%20sizes', 'manual', count)
        products = parseProducts(content)
        count += 1
        totalProducts.extend(products) 
    record(totalProducts)