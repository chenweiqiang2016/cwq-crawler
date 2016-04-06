# -*- coding: utf-8 -*-

# 2016/3/3 使用json抓取联系页面的满意度 但是返回的数据不准 好多为0

import httplib2
import uuid
import os
import re
import json
import sys
import datetime
from pyquery import PyQuery
from utils import extractNum

class Merchant:
    def __init__(self):
        self.attrs = {}
        #self.attrs['category'] = "水龙头";
        
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
        #增加以下字段 诚信经营几年 是否支持支付宝 是否保障
        m['years'] = nodeQ('dd.service > a.icon-goldcxt > em').text()
        m['isAlipay'] = u'是' if nodeQ('dd.service > a.icon-alipay') else u"否"
        m['isTrust'] = u'是' if nodeQ('dd.service > a.icon-trust') else u"否"
        #进入商户页面抓取信息
        parseSupplierContactPage(m)
        merchantList.append(m)
    return merchantList

def parseSupplierContactPage(m):
    #http://yongjia.1688.com/shop/aofudianqi/page/contactinfo.htm?
    if m['url'].find('\?') > 0:
        """do nothing"""
    else:
        if m['url'].endswith("/"):
            m['url'] = m['url'][:-1]
        m['url'] = m['url'] + '?'
    #拼出联系页面的url
    contact_page_url = re.sub("\?.*$", '/page/contactinfo.htm', m['url'])
    content = fetchContent(contact_page_url)
    doc = PyQuery(content)
    #m['satisfication'] = doc('div.detail > div.sat-rate > span.disc > a').text() 动态加载
    if doc('div.detail > div.trade-medal > span.disc > a.image > img').eq(0).attr('alt'):
        m['trade_medal'] = doc('div.detail > div.trade-medal > span.disc > a.image > img').eq(0).attr('alt')
    else:
        m['trade_medal'] = ''
    m['supply-grade'] = len(doc('div.detail > div.supply-grade > span.disc > a.image > img'))
    m['biz-type'] = doc('div.detail > div.biz-type > span').text()
    if not m['biz-type']:
        m['biz-type'] = doc('div.detail > div.smt-biz-type > span').text()
    aList = doc('div.contcat-desc > dl')
    bList = []
    for item in aList:
        itemQ = PyQuery(item)
        text = itemQ.children('dt').text()
        #text = re.sub('\s*','', itemQ.children('dt').text()) #摆不平这个 空格去不掉
        if text.find(u"话") > 0:
            bList.append(itemQ.children('dd').text())
    m['contact'] = ', '.join(bList)
    #根据json数据获取 满意度
    #http://rate.1688.com/stat/trade/winport.json?memberId=aofudianqi&sati=1
    #{"data":{"items":[],"sati":{"satisfactionRate":0,"satisfaction":4.6,"remarkCount":428},"dsr":null},"success":true}
    if re.findall('shop/(.*)/page', contact_page_url):
        stat_url = 'http://rate.1688.com/stat/trade/winport.json?memberId=' + re.findall("shop/(.*)/page", contact_page_url)[0] + '&sati=1'
        content2 = fetchContent(stat_url)
        json_data = json.loads(content2)
        m['satisfication'] = json_data['data']['sati']['satisfaction']
        #抓全部商品数 和 动销 商品数
        #'http://yiwu.1688.com/shop/ywzxbh03/page/offerlist.htm?tradenumFilter=true'
        merchantId=re.findall('shop/(.*)/page', contact_page_url)[0]
        all_products_url = 'http://yiwu.1688.com/shop/' + merchantId + '/page/offerlist.htm?tradenumFilter=true'
        active_product_url = 'http://yiwu.1688.com/shop/' + merchantId + '/page/offerlist.htm'
        content3 = fetchContent(all_products_url)
        doc3 = PyQuery(content3)
        m['products_count'] = extractNum(doc3('li[class="offer-list-tab-title current"] > a > em').text())
        if m['products_count'] == 0:
            m['products_count'] = doc3('ul[data-sp="paging-a"] > li > em.offer-count').text() 
        content4 = fetchContent(active_product_url)
        doc4 = PyQuery(content4)
        m['active_products_count'] = extractNum(doc4('li[class="offer-list-tab-title current"] > a > em').text())
        if m['active_products_count'] == 0:
            m['active_products_count'] = doc4('ul[data-sp="paging-a"] > li > em.offer-count').text() 
    else:
        m['satisfication'] = ''

def persistance(objList, category):
    fields = ['category', 'city', 'name', 'url', 'main_products', 'address', 'satisfaction_rate', 'retention_rates', 'weekly_sales',\
              'years', 'isAlipay', 'isTrust', 'trade_medal', 'supply-grade', 'biz-type','contact', 'satisfication',\
              'products_count', 'active_products_count']
    first_line = '\t'.join(fields) + '\n'
    fw = open(category + '_' + str(datetime.date.today()) + '_' + os.path.basename(__file__).split('.')[0] + "-result.csv", 'w')
    fw.write(first_line)
    for obj in objList:
        datas = []
        for key in fields:
            print key, obj[key]
            if (type(obj[key]) is unicode): #不加外围的括号产生bug
                obj[key] = obj[key].encode("utf-8")
            if (type(obj[key]) is int or type(obj[key]) is float):
                obj[key] = str(obj[key])
            datas.append(obj[key])
        line = '\t'.join(datas) + '\n'
        fw.write(line)
    fw.close()

def parseNextPageUrl(content):
    doc = PyQuery(content)
    if doc('div.page-bottom > a.page-next').attr('href'):
        return "http:" + doc('div.page-bottom > a.page-next').attr('href')

def main(category, start_url):
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
    set_categories(total_merchants, category)
    persistance(total_merchants, category)
    print "WELL DOME"
    
def set_categories(merchants, category):
    for m in merchants:
        m['category'] = category

def main_method_s(category, start_url):
    main(category, start_url)

if __name__ == '__main__': 
    #通过其他脚本来调
    category = sys.argv[1]
    start_url = sys.argv[2]
    #start_url = 'https://ye.1688.com/qiye/-d4b0d2d5b9a4bedf.htm?spm=a360i.cyd0018.0.0.MLvCMk&homeType=1&sortType=SALE_QUANTITY#filt'
    #start_url="https://ye.1688.com/qiye/-bbfac6f7c8cbcde6bedf.htm?spm=a360i.cyd0018.0.0.plX7kd&homeType=1&sortType=SALE_QUANTITY#filt"
    #start_url="https://ye.1688.com/qiye/-b3f8b7bfd0a1b9a4bedf.htm?spm=a360i.cyd0018.0.0.RMoqZC&homeType=1&sortType=SALE_QUANTITY#filt"
    #start_url = "http://ye.1688.com/qiye/-b4b0c1b1.htm?spm=a360i.cyd0018.0.0.30HwlG&homeType=1&sortType=SALE_QUANTITY#filt"
    #start_url = "https://ye.1688.com/qiye/-b3e8ceefd2c2b7fe.htm?spm=a360i.cyd0018.0.0.Tm8FDX&homeType=1&sortType=SALE_QUANTITY#filt"
    
    