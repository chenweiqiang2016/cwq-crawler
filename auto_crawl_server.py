# -*- coding: utf-8 -*-

import pika
import json
import random
import re
import httplib2
import MySQLdb
from pyquery import PyQuery
from utils import extractNum

credentials = pika.PlainCredentials('chenweiqiang', '123456')
parameters = pika.ConnectionParameters('192.168.66.24', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.queue_declare(queue='auto_crawl')

class Db:
    def __init__(self):
        self.connect = MySQLdb.connect(host="192.168.66.24",
                                       user="root",
                                       passwd="test@litb",
                                       db="aims")
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)
    
    def close(self): #关闭cursor
        if self.cursor:
            self.cursor.close()

class Processer:
    def __init__(self):
        self.db = Db()
        
    def extract(self, url):
        #http://www.dx.com/p/h06-multi-function-gms-gps-gprs-vehicle-tracker-black-172624#.VuKnvnqcOjg
        sku_id = ''
        if url.find("dx") > 0:
            sku_id = self.get_sku(url, "-([\d]+)[#$]")
#         elif url.find
        return sku_id
            
    def get_sku(self, url, pattern):
        if re.findall(pattern, url):
            return re.findall(pattern, url)[0]
        return ''
    
    def extractMerchantName(self, url):
        if url.find("dx") > 0:
            return "dx"
        elif url.find("focalprice") > 0:
            return "focalprice"
    
    def getMerchant(self, name):
        sql = """
              select id from merchants where name = %s
        """
        self.db.cursor.execute(sql, name)
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = ""
        return result
    
    def process(self, aList):
        """
                                   错误代码: 3 根据url提取商户名失败
                   5 根据商户名称查询商户id失败
                   7 提取sku_id失败 
                   11 不在products表中
                   17 已经在product_matches中存在              
        """
        litb_id, url = aList[0], aList[1]
        status = 1
        merchantName = self.extractMerchantName(url)
        if not merchantName:
            status = 3
            return status
        merchantId = self.getMerchant(merchantName)
        if not merchantId:
            status = 5
            return status
        sku_id = self.extract(url)
        if not sku_id:
            status = 7
            return status
        #s1: 操作products表
        productId = self.check_in_products(merchantId, sku_id)
        if not productId:
            """
                                             进行抓取, 插入
            """
            product_info = self.get_info_from_crawler(url) #暂时抓img_url, price, category信息 sku_id已知
            if not product_info:
                status = 23 #严重bug, 抓取页面失败
                return status
            productId = self.insert_into_products(product_info[0], product_info[1], sku_id)
            if not productId:
                status = 29 #插入products表失败
                return
        else:
            self.set_products_ctStatus(productId)
            product_info = self.get_info_from_products(productId)
            if not product_info:
                status = 19 #严重bug, 已知id却没有查出products表中的详细情况
                return status
        #s2: 操作product_scores表
        isInProductScores = self.check_in_product_scores(productId)
        if not isInProductScores:
            detail_info = list(product_info) #detail_info = list(product_info).append(merchantId)错误写法
            detail_info.append(merchantId)#detail_info.append(merchantId).append(productId)
            detail_info.append(productId)
            self.insert_into_product_scores(detail_info)
        else:
            #暂时不考虑不更新价格, 只更新ct_status
            self.set_product_scores_ctStatus(productId)
        #s3: 操作product_matches表
        isInProductMatches = self.check_in_product_matches(productId, litb_id)
        if not isInProductMatches:
            self.insert_into_product_matches(merchantId, litb_id, productId)
        else:
            status = status * 17
        return status

    def check_in_products(self, merchantId, sku_id):
        sql = """select id from products where merchant_id=%s and sku_id=%s"""
        self.db.cursor.execute(sql, (merchantId, sku_id))
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = None
        return result
    
    def get_info_from_products(self, productId):
        sql = """select name, category_id, price from products where id=%s"""
        self.db.cursor.execute(sql, productId)
        try:
            result = self.db.cursor.fetchone()
        except:
            result = []
        return result
    
    def set_products_ctStatus(self, productId):
        sql = """update products set ct_status=4 where id=%s"""
        self.db.cursor.execute(sql, productId)
    
    def get_info_from_crawler(self, url, merchantId, merchantName):
        content = self.fetch_page_content(url)
        doc = PyQuery(content)
        if merchantName == 'dx':
            name = doc("h1 > span#headline").text()
            price = doc("span#price").text()
#             categoryList = []
#             categoryNodeList = doc("div.wrapper > div.position > a")
#             for node in categoryNodeList:
#                 nodeQ = PyQuery(node)
#                 categoryList.append(nodeQ.text().strip()) if nodeQ.text().strip() else """do nothing"""
        return [name, price]
    
    def insert_into_products(self, name, price, merchant_id, sku_id):
        sql1 = """insert into products (name, price, merchant_id, sku_id, ct_status) values (%s, %s, %s, %s, 4)"""
        sql2 = """select id from products where merchant_id=%s and sku_id=%s"""
        self.db.cursor.execute(sql1, (name, price, merchant_id, sku_id))
        self.db.cursor.execute(sql2, (merchant_id, sku_id))
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = ''
        return result

    def fetch_page_content(self, url):
        h = httplib2.Http()
        response, content = h.request(url)
        if response.status == 200:
            return content
    
    def check_in_product_scores(self, productId):
        sql = """select product_id from product_scores where product_id=%s"""
        self.db.cursor.execute(sql, productId)
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = None
        return True if result else False
    
    def insert_into_product_scores(self, product_info_list):
        sql1 = """insert into product_scores (product_name, category_id, price, merchant_id, product_id, ct_status, score) values (%s, %s, %s, %s, %s, 4, 0.08)"""
        sql2 = """insert into product_scores (product_name, price, merchant_id, product_id, ct_status, score) values (%s, %s, %s, %s, 4, 0.08)"""
        product_info_list[2] = float(extractNum(product_info_list[2])) #scores表中price是double
        if len(product_info_list) == 5:
            self.db.cursor.execute(sql1, product_info_list)
        if len(product_info_list) == 4:
            self.db.cursor.execute(sql2, product_info_list)

    def set_product_scores_ctStatus(self, productId):
        sql = """update product_scores set ct_status=4 where product_id=%s"""
        self.db.cursor.execute(sql, productId)
        
    def check_in_product_matches(self, productId, litb_id):
        sql = """select * from product_matches where product_id=%s and litb_product_id=%s"""
        self.db.cursor.execute(sql, (productId, litb_id))
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = None
        return True if result else False
    
    def insert_into_product_matches(self, merchantId, litb_id, productId):
        sql = """insert into product_matches (merchant_id, litb_product_id, product_id) values (%s, %s, %s)"""
        self.db.cursor.execute(sql, (merchantId, litb_id, productId))

processer = Processer()

def process(info):
    """
       info: 包含 litb_id 和 竞争对手  url
    """
    litb_id, url = info.split(';')[0].strip(), info.split(';')[1].strip()
    print u'兰亭id是:', litb_id
    print u'对手url是:', url
    #s1: 提取出商户和sku_id
    #s2: 抓取价格信息
    #s3: 保存关联关系到product_matches表
    #s4: 保存商品信息到products表和product_scores表
    status = processer.process([litb_id, url])
    if status in [3, 5]:
        return json.dumps({'status': 0, 'reason': '新的商户不能支持'})
    elif status in [7]:
        return json.dumps({'status': 0, 'reason': '已有商户操作异常'})
    else:
        return json.dumps({'status': 1, 'reason': ''})

def on_request(ch, method, props, body):

    print(" [.] process(%s)" % body)
    response = process(body)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='auto_crawl')

print(" [x] Awaiting <litb product id> and <competitor's product url> to come...")
channel.start_consuming()