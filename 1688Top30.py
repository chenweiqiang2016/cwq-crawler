# -*- coding: utf-8 -*-

import os
import re
import datetime
import xlrd
import urllib
from products import main, set_categories
from productsPerMerchant import crawlProducts, process_url

DEFAULT_STR_LIST = []
DEFAULT_PATH = '.'

def find_files(path=DEFAULT_PATH, str_list=DEFAULT_STR_LIST):
    file_list = os.listdir(path) #不是完整的路径
    result_file_list = []
    if len(file_list) > 0:
        for file in file_list:
            if len(str_list) > 0:
                if has_substr_list(str_list, file):
                  result_file_list.append(os.path.join(path, file))  
            else:
                result_file_list.append(os.path.join(path, file))
    return result_file_list

def has_substr_list(str_list, file):
    for substr in str_list:
        if substr not in file:
            return False
    return True

def init_file(output_dir='E:'):
    fw = open(output_dir + "1688_" + datetime.date.today().strftime("%m-%d-%Y") + "_productInfo.csv", 'w')
    headers = ['level1_category', 'name', 'product_url', 'img_url', 'price', 'reviews', 'sku_id']
    fw.write('\t'.join(headers) + '\n')
    return fw

def process(wf, filename):
    wb = xlrd.open_workbook(filename)
    ws = wb.sheets()[0]
    rows = ws.nrows
    cols = ws.ncols
    url_idx = ws.row_values(0).index('url')
    count = 0
    #简单粗暴查找关键词
    keywords = ws.cell(1, 0).value
    print keywords
    if not keywords:
        keywords = ws.cell(2, 0).value
    
    for row in range(1, rows):
        if ws.cell(row, cols-1).value.strip() == '':
            continue
        else:
            count += 1
            print 'crawl %dth line ... (%d of 6)' %(row, count)
            merchant_url = ws.cell(row, url_idx).value
            try:
                crawl_url = get_crawl_url(merchant_url, keywords)
                print crawl_url
                productList = crawl_products(crawl_url)
                for product in productList:
                    #headers: ['level1_category', 'name', 'product_url', 'img_url', 'price', 'reviews', 'sku_id']
                    #返回的数据: name, product_url, img_url, price, tags, sold
                    sku_id = re.findall('/([\d]+)\.html', product[1])[0]
                    datas = [keywords, product[0], process_url(product[1]), product[2], product[3], str(product[5]), sku_id]
                    for idx, data in enumerate(datas):
                        if type(data) is unicode:
                            datas[idx] = data.encode('utf-8')
                    wf.write('\t'.join(datas) + '\n')
            except Exception, e:
                "REEOR: fail to crawl merchant {" + merchant_url + "}"
                print e

def get_crawl_url(merchant_url, keywords):
    #http://nanan.1688.com/shop/shop1435597141657/page/offerlist.htm?keywords=%CB%AE%C1%FA%CD%B7
    merchant_id = get_merchant_id(merchant_url)
    crawl_url = merchant_url[0:merchant_url.find(merchant_id)] + merchant_id + "/page/offerlist.htm"
    d = {"keywords": keywords.encode('gb2312')} #适当时候应该修改
    q = urllib.urlencode(d)
    return crawl_url + '?' + q
    
def get_merchant_id(url):
    return re.findall("shop/[\w]+", url)[0]

def crawl_products(url):
    productList = crawlProducts(url, 2) #每页24, 抓2页
    return productList[:30] if len(productList) > 30 else productList

if __name__ == '__main__':
    xls_files = find_files("E:", ['xls', 'new'])
    
    wf = init_file()
    
    for file in xls_files:
        process(wf, file)
        
    wf.close()
