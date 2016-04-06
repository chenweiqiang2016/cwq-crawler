# -*- coding: utf-8 -*-

import xlwt
import xlrd
from pyquery import PyQuery
from utils import fetchPageWithUrl, extractNum

urls = []

def get_urls():
    pass

def iterator_merchants():
    pass

def crawlProductsByMerchant():
    pass

def get_categories(url):
    content = fetchPageWithUrl(url)
    cate_list = []
    if content:
        doc = PyQuery(content)
        categoryNodeList = doc("div.wp-category-nav-unit > ul > li > a")
        for node in categoryNodeList:
            url, num, name= PyQuery(node).attr('href'), PyQuery(node)('span').text(), PyQuery(node).remove('span').text()
            cate_list.append([url, name, num])
    return cate_list

def crawlProductsByCategory(cate_list, ws, merchant_info):
    row = 1
    for index, atuple in enumerate(cate_list):
        try:
            cate_num = extractNum(atuple[2])
            products = crawlProducts(atuple[0])
            for product in products:
                #这六个是店铺信息
                ws.write(row, 0, merchant_info[0])
                ws.write(row, 1, merchant_info[1])
                ws.write(row, 2, merchant_info[2])
                ws.write(row, 3, merchant_info[3])
                ws.write(row, 4, merchant_info[4])
                ws.write(row, 5, merchant_info[5])
                #店铺内一级品类
                ws.write(row, 6, atuple[1])
                #该品类数目
                ws.write(row, 7, cate_num)
                #抓取的商品信息 [name, product_url, img_url, price, tags, sold]
                ws.write(row, 8, product[0])
                ws.write(row, 9, product[1])
                ws.write(row, 10, product[2])
                ws.write(row, 11, product[3])
                ws.write(row, 12, product[4])
                ws.write(row, 13, str(product[5]))
                row += 1
        except Exception, e:
            print e
            print 'category', (index + 1), "of", len(cate_list), "failed!"

def crawlProducts(start_url, limit=999):
    current_url = start_url
    products = []
    page_count = 1
    total_count = 0 #全部商品数目
    while True:
        content = fetchPageWithUrl(current_url)
        print 'fetch page %s' %page_count
        if not content:
            break
        doc = PyQuery(content)
        nodeList = PyQuery(doc('div[data-tracelog-exp="wp_widget_offerhand_main_disp"]').eq(0))('ul.offer-list-row > li')#PyQuery(doc('div.common-column-150').eq(0))('ul.offer-list-row > li') #common-column-220
        if len(nodeList) < 4:
           print len(nodeList)
        for num, node in enumerate(nodeList):
            nodeQ = PyQuery(node)
            name = nodeQ('div.title > a').attr('title')
            product_url = nodeQ('div.title > a').attr('href')
            img_url = "http:" + nodeQ('div.image > a > img').attr('data-lazy-load-src')
            price = nodeQ('div.price').text()
            if nodeQ('div.attributes > span'):
                tags = ''
                for tagNode in nodeQ('div.attributes > span'):
                    tagNodeQ = PyQuery(tagNode)
                    text = tagNodeQ.attr('class')
                    tags = tags + ' ' + text
            else:
                tags = ''
            sold = extractNum(nodeQ('div.booked-count').text())
            total_count += 1
            products.append([name, product_url, img_url, price, tags, sold, page_count, num+1, total_count])
        next_url = parse_next_url(doc)
        if not next_url:
            break
        current_url = process_url(next_url)
        page_count += 1
        if page_count > limit:
            break
    return products

def process_url(url):
    if url.find("http") == 0:
        return url
    elif url.find("://") == 0:
        return "http" + url
    elif url.find("//") == 0:
        return "http:" + url
    return url

def parse_next_url(contentQ):
    if contentQ('li.pagination > a.next-disabled'):
        return None
    if contentQ('li.pagination > a.next').attr('href'):
        return contentQ('li.pagination > a.next').attr('href')
    
def get_categories_url(home_url):
    content = fetchPageWithUrl(home_url)
    doc = PyQuery(content)
    return doc('a.show-category').attr('href')

def init_ws(ws):
    ws.write(0, 0, 'merchant_category')
    ws.write(0, 1, 'merchant_name')   
    ws.write(0, 2, 'merchant_url')
    ws.write(0, 3, 'merchant_main_products')
    ws.write(0, 4, 'merchant_contact')
    ws.write(0, 5, 'merchant_weekly_sales')
    ws.write(0, 6, 'level1_category')
    ws.write(0, 7, 'show_cate_num')
    ws.write(0, 8, 'product_name')
    ws.write(0, 9, 'product_url')
    ws.write(0, 10, 'product_img_url')
    ws.write(0, 11, 'price')
    ws.write(0, 12, 'product_tags')
    ws.write(0, 13, 'product_sold')

if __name__ == '__main__':
    rb = xlrd.open_workbook('a.xls')
    rs = rb.sheets()[0]
    wb = xlwt.Workbook(encoding='utf-8')
    #category, name, url, main_products, contact, weekly_sales
    for row in range(1, 21):
        try:
            merchant_info = [rs.cell(row, 0).value, rs.cell(row, 2).value, rs.cell(row, 3).value, rs.cell(row, 4).value, rs.cell(row, 15).value, rs.cell(row, 8).value]
            print 'begin to process', str(row) + 'rd', 'merchant... [%s]' %merchant_info[2]
            #print merchant_info
            cates_url = get_categories_url(merchant_info[2])
            #print cates_url
            cates = get_categories(cates_url)
            ws = wb.add_sheet('sheet' + str(row))
            init_ws(ws)
            crawlProductsByCategory(cates, ws, merchant_info)
        except Exception, e:
            print e
            print (row + 1), "of 20 merchants failed!"
    wb.save('b.xls')
    print 'well done.'