# -*-coding: utf-8 -*-

from products import *
from suppliers import *

# category=u'厨卫 '
# start_url='https://ye.1688.com/chanpin/-d4b0d2d5b9e0b8c8.htm?spm=a360i.cyd0017.0.0.XQ4lUU&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt'
# total_products = main(start_url, 5)
# set_categories(total_products, category)
# persistance(total_products, category)
# print "WELL DOME"

def batch_crawl(filename):
    fr = open(filename)
    while True:
        category = fr.readline().strip()
        if not category:
            break
        else:
            print category

def manual_crawl():
    category_list = [u'水龙头', u'园艺工具', u'园艺灌溉', u'园艺装饰', u'窗帘', u'四件套', u'厨房', u'灯', u'装饰画', u'卫浴挂件', u'挂钟', u'摆件']
    producturl_list = ['https://ye.1688.com/chanpin/-cbaec1facdb7.htm?spm=a360i.cyd0017.0.0.khJ0G5&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-d4b0d2d5b9a4bedf.htm?spm=a360i.cyd0017.0.07eFvni&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-d4b0d2d5b9e0b8c8.htm?spm=a360i.cyd0017.0.0.NChh3L&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-d4b0d2d5d7b0cace.htm?spm=a360i.cyd0017.0.0.y3WiXN&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-b4b0c1b1.htm?spm=a360i.cyd0017.0.0.KZgwvi&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-cbc4bcfeccd7.htm?spm=a360i.cyd0017.0.0.xemJ0W&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-b3f8b7bf.htm?spm=a360i.cyd0017.0.0.rCO5oN&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-b5c6.htm?spm=a360i.cyd0017.0.0.VB83u0&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-d7b0cacebbad.htm?spm=a360i.cyd0017.0.0.FFeAEr&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-cec0d4a1b9d2bcfe.htm?spm=a360i.cyd0017.0.0.gmcbWk&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-b9d2d6d3.htm?spm=a360i.cyd0017.0.0.qz3HuH&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt', \
'https://ye.1688.com/chanpin/-b0dabcfe.htm?spm=a360i.cyd0017.0.0.9vaJZx&homeType=1&analy=n&newProduct=1&sortType=MLR_PAY_COUNT&sortOrder=DESC#filt']

    merchanturl_list = ['https://ye.1688.com/qiye/-cbaec1facdb7.htm?spm=a360i.cyd0018.0.0.TGyUem&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-d4b0d2d5b9a4bedf.htm?spm=a360i.cyd0018.0.0.HH61h3&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-d4b0d2d5b9e0b8c8.htm?spm=a360i.cyd0018.0.0.L2aXPG&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-d4b0d2d5d7b0cace.htm?spm=a360i.cyd0018.0.0.zv5uvv&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-b4b0c1b1.htm?spm=a360i.cyd0018.0.0.ykyRUJ&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-cbc4bcfeccd7.htm?spm=a360i.cyd0018.0.0.AwaUum&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-b3f8b7bf.htm?spm=a360i.cyd0018.0.0.eJXDZ2&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-b5c6.htm?spm=a360i.cyd0018.0.0.Vz7EPo&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-d7b0cacebbad.htm?spm=a360i.cyd0018.0.0.L9RKGq&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-cec0d4a1b9d2bcfe.htm?spm=a360i.cyd0018.0.0.z0L9oa&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-b9d2d6d3.htm?spm=a360i.cyd0018.0.0.4cVHzO&homeType=1&sortType=SALE_QUANTITY#filt', \
'https://ye.1688.com/qiye/-b0dabcfe.htm?spm=a360i.cyd0018.0.0.Nqo5Wd&homeType=1&sortType=SALE_QUANTITY#filt']

    for index, category in enumerate(category_list):
        if index != 3:
            continue
        crawl_products_and_categories(category, producturl_list[index], merchanturl_list[index])
        
def crawl_products_and_categories(category, product_url, merchant_url):
    main_method_p(category, product_url)
    main_method_s(category, merchant_url) 

if __name__ == '__main__':
    filename = 'E:categories.csv'
    #batch_crawl(filename)
    manual_crawl()