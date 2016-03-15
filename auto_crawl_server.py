# -*- coding: utf-8 -*-

import pika
import json
import random
import re
import httplib2
import datetime
import MySQLdb
from pyquery import PyQuery
from utils import extractNum
from various_merchants import extract, extractMerchantName, get_info_from_crawler

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
        merchantName = extractMerchantName(url)
        if not merchantName:
            status = 3
            return status
        merchantId = self.getMerchant(merchantName)
        if not merchantId:
            status = 5
            return status
        sku_id = extract(url)
        if not sku_id:
            status = 7
            return status
        #s1: 操作products表
        productId = self.check_in_products(merchantId, sku_id)
        if not productId:
            """
                                             进行抓取, 插入
            """
            try:
                product_info = get_info_from_crawler(url, merchantName) #暂时抓img_url, price, category信息 sku_id已知
            except:
                status = 23 #严重bug, 抓取页面失败
                return status
            productId = self.insert_into_products(product_info[0], product_info[1], product_info[2], url, merchantId, sku_id)
            if not productId:
                status = 29 #插入products表失败
                return status
        else:
            self.set_products_ctStatus(productId)
            product_info = self.get_info_from_products(productId) #获取的字段 name, category_id, price, img_url
            if not product_info:
                status = 19 #严重bug, 已知id却没有查出products表中的详细情况
                return status
        #s2: 操作product_scores表
        isInProductScores = self.check_in_product_scores(productId)
        if not isInProductScores:
            detail_info = list(product_info) #detail_info = list(product_info).append(merchantId)错误写法
            detail_info.append(merchantId)#detail_info.append(merchantId).append(productId)
            detail_info.append(productId)
            detail_info.append(url)
            try:
                self.insert_into_product_scores(detail_info)
            except:
                status = 31
                return status
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
        sql = """select name, category_id, price, img_url from products where id=%s"""
        self.db.cursor.execute(sql, productId)
        try:
            result = self.db.cursor.fetchone()
        except:
            result = []
        return result
    
    def set_products_ctStatus(self, productId):
        sql = """update products set ct_status=4 where id=%s"""
        self.db.cursor.execute(sql, productId)
    
    def insert_into_products(self, name, price, img_url, product_url, merchant_id, sku_id):
        sql1 = """insert into products (name, price, merchant_id, img_url, url, sku_id, ct_status) values (%s, %s, %s, %s, %s, %s, 4)"""
        sql2 = """select id from products where merchant_id=%s and sku_id=%s"""
        self.db.cursor.execute(sql1, (name, price, merchant_id, img_url, product_url, sku_id))
        self.db.cursor.execute(sql2, (merchant_id, sku_id))
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = ''
        return result

    def check_in_product_scores(self, productId):
        sql = """select product_id from product_scores where product_id=%s"""
        self.db.cursor.execute(sql, productId)
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = None
        return True if result else False      
                                                            #[name, price, img_url, merchantId, productId, url]
    def insert_into_product_scores(self, product_info_list):#[name, category_id, price, img_url, merchantId, productId, url]
        day = datetime.date.today().strftime("%Y-%m-%d")
        sql1 = """insert into product_scores (product_name, category_id, price, img_url, merchant_id, product_id, product_url, ct_status, score, calc_date, score_type) values (%s, %s, %s, %s, %s, %s, %s, 4, 0.08, %s, 'HUMAN_SET')"""
        sql2 = """insert into product_scores (product_name, price, img_url, merchant_id, product_id, product_url, ct_status, score, calc_date, score_type) values (%s, %s, %s, %s, %s, %s, 4, 0.08, %s, 'HUMAN_SET')"""
        if len(product_info_list) == 7:
            product_info_list[2] = float(extractNum(product_info_list[2])) #scores表中price是double
            product_info_list.append(day)
            self.db.cursor.execute(sql1, product_info_list)
        if len(product_info_list) == 6:
            product_info_list[1] = float(extractNum(product_info_list[1])) #scores表中price是double
            product_info_list.append(day)
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

#在本端进行测试
def test():
    processer.process(["123456", "http://www.ebay.com/itm/Genuine-Shark-New-Silver-Case-Date-Day-Leather-Quartz-Sport-Wrist-Watch-/350794635597"])

test()

def process(info):
    """
       info: 包含 litb_id 和 竞争对手  url
    """
    litb_id, url = info.split(';')[0].strip(), info.split(';')[1].strip()
    print u'兰亭id是:', litb_id
    print u'对手url是:', url
    status = processer.process([litb_id, url])
    if status in [3, 5]:
        return json.dumps({'status': 0, 'reason': '新的商户不能支持'})
    elif status in [7, 23, 31]:
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