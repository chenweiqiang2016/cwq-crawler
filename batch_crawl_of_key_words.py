#-*- coding: utf-8 -*-
"""
          读取excel, 逐次抓取每个关键词的一定数目的top商品
         每个关键词的top商品对应一个文件, 文件名以关键词进行区分
"""
import xlrd
import xlwt
import os
import re
import httplib2
from pyquery import PyQuery
from utils import extractNum

default_prefix = "C:/users/chenweiqiang/Desktop/"

keys = []

def get_keys(filename, prefix=default_prefix):
    file = os.path.join(prefix, filename)
    wb = xlrd.open_workbook(file)
    ws = wb.sheets()[0]
    for index in range(1, ws.nrows):
        keys.append(ws.cell(index, 0).value)

def iterator(merchants):
    amazon_base1="http://www.amazon.com/s/ref=nb_sb_noss?keywords="
    amazon_base2="&sort=review-rank"
    aliexpress_base1="http://www.aliexpress.com/wholesale?SearchText="
    aliexpress_base2="&shipCountry=us&SortType=total_tranpro_desc&g=n"
    dhgate_base1="http://www.dhgate.com/wholesale/search.do?searchkey="
    dhgate_base2="&searchSource=sort&stype=down&sinfo=reviewavgscore"
    for item in keys:
        if 'amazon' in merchants:
            amazon_url = amazon_base1 + item.replace(" ", "+") + amazon_base2
            process_amazon(amazon_url, item)
        if 'aliexpress' in merchants:
            aliexpress_url = aliexpress_base1 + item.replace(" ", "+") + aliexpress_base2
            process_aliexpress(aliexpress_url, item)
        if 'dhgate' in merchants:
            dhgate_url = dhgate_base1 + item.replace(" ", "+") + dhgate_base2
            process_dhgate(dhgate_url, item)

def process_amazon(entance_url, item):
    current_url = entance_url
    count = 0
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("sheet1")
    ws.write(0,0,"name")
    ws.write(0,1,"price")
    ws.write(0,2,"product_url")
    ws.write(0,3,"img_url")
    ws.write(0,4,"reviews")
    while True:
        content = fetch_page_content(current_url)
        doc = PyQuery(content)
        nodeList = doc("div#atfResults > ul#s-results-list-atf > li") #前六个
        nodeList_other = doc('div#btfResults > ul > li')
        nodeList.extend(nodeList_other)
        for node in nodeList:
            nodeQ = PyQuery(node)
            name = nodeQ('h2').parent('a').attr('title')
            product_url = nodeQ('h2').parent('a').attr('href')
            img_url = nodeQ('img.s-access-image').attr('src')
            price = nodeQ('span.s-price').text()
            reviews = nodeQ('div[class="a-row a-spacing-mini"] > a[class="a-size-small a-link-normal a-text-normal"]').remove('span').text()
            if not reviews:
                reviews = nodeQ('div[class="a-row a-spacing-top-mini a-spacing-none"] > a[class="a-size-small a-link-normal a-text-normal"]').remove('span').text()
            reviews = re.sub("See.*",'', reviews).strip()
            count += 1
            ws.write(count,0,name)
            ws.write(count,1,price)
            ws.write(count,2,product_url)
            ws.write(count,3,img_url)
            ws.write(count,4,reviews)
        current_url = parseNextPage(doc, current_url)
        if count >= 100:
            break
    wb.save("./output/amazon-" + item + ".xls")

def process_aliexpress(entance_url, item):
    current_url = entance_url
    count = 0
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("sheet1")
    ws.write(0,0,"name")
    ws.write(0,1,"price")
    ws.write(0,2,"product_url")
    ws.write(0,3,"img_url")
    ws.write(0,4,"reviews")
    ws.write(0,5,"sold")
    while True:
        content = fetch_page_content(current_url)
        doc = PyQuery(content)
        #失败: http://www.aliexpress.com/wholesale?SearchText=wall+clock&shipCountry=us&SortType=total_tranpro_desc
        nodeList = doc("li.list-item") #只能获取3个
        doc_part = PyQuery(doc('script#lazy-render').text())
        otherNodeList = doc_part("li.list-item")
        nodeList.extend(otherNodeList)
        for node in nodeList:
            nodeQ = PyQuery(node)
            name = nodeQ('div.detail > h3 > a').eq(0).attr('title')
            product_url = nodeQ('div.detail> h3 > a').eq(0).attr('href')
            img_url = nodeQ('div.img > a > img.picCore').attr('src')
            price = nodeQ('span.price').text()
            reviews = extractNum(nodeQ('div.rate-history > a[class="rate-num "]').text())
            orders = extractNum(nodeQ('a[class="order-num-a "] > em').text())
            count += 1
            ws.write(count,0,name)
            ws.write(count,1,price)
            ws.write(count,2,product_url)
            ws.write(count,3,img_url)
            ws.write(count,4,reviews)
            ws.write(count,5,orders)
        current_url = parseAliexpressNextPageUrl(doc, current_url)
        if count >= 100:
            break
    wb.save("./output/aliexpress-" + item + ".xls")

def process_dhgate(entance_url, item):
    current_url = entance_url
    count = 0
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("sheet1")
    ws.write(0,0,"name")
    ws.write(0,1,"price")
    ws.write(0,2,"product_url")
    ws.write(0,3,"img_url")
    ws.write(0,4,"reviews")
    ws.write(0,5,"sold")
    while True:
        if not current_url:
            break
        content = fetch_page_content(current_url)
        doc = PyQuery(content)
        nodeList = doc("div.listitem")
        for node in nodeList:
            nodeQ = PyQuery(node)
            name = nodeQ('h3.pro-title > a').text()
            product_url = nodeQ('h3.pro-title > a').attr('href')
            img_url = nodeQ('div.photo > a.pic > img').attr('src')
            price = nodeQ('ul.pricewrap > li.price').text()
            reviews = extractNum(nodeQ('span.reviewnum').text())
            spanList = nodeQ('span')
            orders = None
            for span in spanList:
                spanQ = PyQuery(span)
                if spanQ.text().startswith("Sold"):
                    orders = extractNum(spanQ.text())
            count += 1
            ws.write(count,0,name)
            ws.write(count,1,price)
            ws.write(count,2,product_url)
            ws.write(count,3,img_url)
            ws.write(count,4,reviews)
            ws.write(count,5,orders)
        current_url = parseDhgateNextPageUrl(doc, current_url)
        if count >= 100:
            break
    wb.save("./output/dhgate-" + item + ".xls")

def parseNextPage(doc, url):
    return "http://www.amazon.com" + doc('a#pagnNextLink').attr('href')

def parseAliexpressNextPageUrl(doc, url):
    return doc('a.page-next').attr('href')

def parseDhgateNextPageUrl(doc, url):
    return doc('a.next').attr('href')

def fetch_page_content(url): 
    h = httplib2.Http()
    response, content = h.request(url)
    if response.status == 200:
        return content

if __name__ == '__main__':
    #merchants = ['amazon', 'aliexpress', 'dhgate']
    merchants = ['dhgate']
    get_keys(u'Homer Dector CT关键词.xlsx') #必须加u
    iterator(merchants)

