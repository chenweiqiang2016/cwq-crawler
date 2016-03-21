# -*- coding: utf-8 -*-

# 用于抓取1688图片

import xlrd
import re
import urllib
import httplib2
from pyquery import PyQuery

def extract_skuId(url):
    try:
        return re.findall('offer/(\d+)\.html', url)[0]
    except:
        return ''

def fetch_page_content(url):
    h = httplib2.Http()
    response, content = h.request(url)
    if response.status == 200:
        return content

def get_img_urls(content):
    if not content:
        return []
    url_list = []
    doc = PyQuery(content)
    nodeList = doc('li.tab-trigger > div.vertical-img > a.box-img > img')
    for node in nodeList:
        url = PyQuery(node).attr('src')
        if not url:
            continue
        if url.find('60x60') > 0:
            url=url.replace('60x60','400x400')
            url_list.append(url)
    return url_list
    

def download(img_url, sku_id, index):
    path = './output/' + str(sku_id) + '_' + str(index+1) + '.jpg'
    conn = urllib.urlopen(img_url)  
    f = open(path,'wb')  
    f.write(conn.read())  
    f.close()
    
if __name__ == '__main__':
    wb = xlrd.open_workbook("1688products-result.xls")
    ws = wb.sheets()[0]
    headers = ws.row_values(0)
    url_index = headers.index("product_url")
    for row in range(1, ws.nrows):
        print "(Downloading " + str(row) + " of " + str(ws.nrows-1) + ")",
        product_url = ws.cell(row, url_index).value
        sku_id = extract_skuId(product_url)
        print sku_id, "[" + product_url + "]" 
        if not sku_id:
            continue
        content = fetch_page_content(product_url)
        img_urls = get_img_urls(content)
        for index, img_url in enumerate(img_urls):
            download(img_url, sku_id, index)
