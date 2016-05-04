# -*- coding: utf-8 -*-

# 一个初步的版本 可以抓取1688商品 存在一个访问bug L190 一个页面三次异步加载的数据没处理

import httplib2
import uuid
import os
import random
import time
import sys
import re
import datetime
from pyquery import PyQuery
from utils import extractNum
from pics_1688 import get_img_urls


# class OneSixDoubleEightParser:
#     def crawlProducts(self, page):
#         doc = PyQuery(page)
#         
#     
#     def parseNextPageUrl(self, page):
#         doc = PyQuery(page)
#         doc('span.fui-paging-list > a.fui-next').text()


headers = ['level1_category', 'level2_category', 'level3_category',\
           'sku_id', 'product_name', 'product_price', 'product_url',\
           'img_url', 'img_urls', 'size', 'color', 'update_time', 'store_name',\
           'store_url', 'store_address', 'qq', 'telephone', 'supplier_name',\
           'city', 'reviews', 'tags', 'total_sales', 'monthly_sales']

current_url2 = 'https://s.1688.com/selloffer/-CAD6BBFAB1A3BBA4C4A4-1033986.html?spm=a262l.22849.1998916260.9.816HeX#beginPage=1&offset=9&filterP4pIds=40017869659,44043851593,527780756099,43575315465,40564214806,42969161522,44304416622,37820169122'

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

def fetchContent(url, saveFile=True, headers={}):
#     sleep();
    h = httplib2.Http()
    h.follow_redirects = False
    response, content = h.request(url, method='GET' ,headers=headers)
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
    productNodeList = doc('ul#sm-offer-list > li')
    productList = []
    for node in productNodeList:
        nodeQ = PyQuery(node)
        p = Product()
        p['product_name'] = nodeQ('a[offer-stat="title"]').text()
        url = nodeQ('a[offer-stat="title"]').attr('href')
        if url.find('http') == 0:
            p['product_url'] = url
        else:    
            p['product_url'] = "http:" + url
        p['product_price'] = nodeQ('span.sm-offer-priceNum').text()
        p['img_url'] = nodeQ('a[offer-stat="pic"] > img').attr('src')
        p['sku_id'] = nodeQ.attr('t-offer-id')

        p['store_name'] =  nodeQ('a.sm-offer-companyName').text()
        p['store_url'] = nodeQ('a.sm-offer-companyName').attr('href')
        print p['store_url']
        p['tags'] = []
        aList = nodeQ("div.sm-offer-subicon > a")
        for a in aList:
            s = PyQuery(a).attr('class')
            if s:
                p['tags'].append(s)
        p['tags'] = ', '.join(p['tags'])
#         parseProductPage(p, True)
#         parseStorePage(p)
#         productList.append(p)
        #return productList #测试
    return productList

def parseProductPage(product, need_img_urls=False):
    """进入商品详情页, 抓取四个新字段
       delivery reviews star total_sales
    """
    if product['sku_id']:
       content = fetchContent("https://detail.1688.com/offer/" + product['sku_id'] + ".html")
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
    return product

store_info = {}

def parseStorePage(product):
    store_url = product['store_url']
    index = store_url.find('1688.com')
    store_url = store_url[:index]
    contact_url = store_url + '1688.com/page/contactinfo.htm'
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
           print nodeQ.children('dt').text()
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
    fields = ['level1_category', 'level2_category', 'level3_category',\
           'sku_id', 'product_name', 'product_price', 'product_url',\
           'img_url', 'img_urls', 'size', 'color', 'store_name',\
           'store_url', 'store_address', 'mobile', 'telephone', 'supplier_name',\
           'city', 'reviews', 'tags', 'total_sales']

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
    print current_url2
    pageNum = re.findall('beginPage=(\d+)', current_url2)[0]
    newPageNum = str(int(pageNum) + 1)
    current_url2 = current_url2.replace('beginPage='+pageNum, 'beginPage='+newPageNum)
    #current_url = url
    return current_url2
#     if doc('div.page-bottom > a.page-next').attr('href'):
#         return "http:" + doc('div.page-bottom > a.page-next').attr('href')

def main(start_url, limit):
    """完成各个方法的调度"""
    url = start_url
    LIMIT = limit #LIMIT = 5 #抓5个页面
    count = 1
    total_products = []
    while count <= LIMIT:
        headers = {'Host': 's.1688.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br', 'Cookie': 'ali_beacon_id=106.39.48.34.1459410332938.834757.0; cna=GG2CD8ixoU0CAWonMCIb2MvX; alicnweb=touch_tb_at%3D1460514330654%7Clastlogonid%3D%25E7%2582%258E%25E9%25BE%2599%25E4%25BE%25A0%25E5%2593%25A5%25E5%2593%25A5%7Cshow_inter_tips%3Dfalse; isg=AAE822F8DD05B5600553C95E0BACFD87; l=AkREMnhnDJ3OKxhV7FBX8joMNMg2XWjH; ali_ab=106.39.48.34.1459412602224.3; __last_loginid__=%E7%82%8E%E9%BE%99%E4%BE%A0%E5%93%A5%E5%93%A5; __cn_logon__=true; last_mid=b2b-911619735pocrk; ali_apache_track="c_ms=1|c_mid=b2b-911619735pocrk|c_lid=%E7%82%8E%E9%BE%99%E4%BE%A0%E5%93%A5%E5%93%A5"; _cn_slid_=0f6eeJNEJK; ad_prefer="2016/04/13 11:07:15"; h_keys="%u624b%u673a%u4fdd%u62a4%u819c#%u8fde%u8863%u88d9#%u5ba0%u7269%u8863%u670d"; alisw=swIs1200%3D1%7C; __cn_logon_id__=%E7%82%8E%E9%BE%99%E4%BE%A0%E5%93%A5%E5%93%A5; JSESSIONID=8L78HCBZ1-9WVV3YAFC43Nl3Eq77-pj9aDiP-po; _tmp_ck_0="AhAPwLGenDuHUS1FlsrQoHCyXiiExdP08RIFhzO%2FGZGOnHekCfjRxkRR6%2FrZ6SUdpkGXZSfrS9zTEVNe6mokVurN4qv9mRA%2BACj5tjhQa612%2BdKEv4nP04ZCoyYorORKF%2FE3rKAWyKy0mS8oTbWVn%2FbQEL8YrQYfDRxHLvUs5Jw%2BInaZIDpvyaVaTMAk8MDysLVNQ6VK3HY1cnKN5P6JakymS10OnJRAIM2IXYZBUm8eFT9JWZebIn7xCVtg9pDcbp8bgwaFNBVJGaCM5wV6zV6XwVHYJZFfzHxnY5hRr38L0lCy7kchozuya2iPfFBkoAbi2VoGOX%2FeNSVEjkc7MQ%3D%3D"', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0'}
        content = fetchContent(url, headers=headers)
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
    total_products = main(start_url, 5)
    set_categories(total_products, category)
    persistance(total_products, category)
    print "WELL DOME"

if __name__ == '__main__':
    category = u'手机保护膜'
    start_url = 'https://s.1688.com/selloffer/-CAD6BBFAB1A3BBA4C4A4-1033986.html?spm=a262l.22849.1998916260.9.816HeX'
    main_method_p(category, start_url)