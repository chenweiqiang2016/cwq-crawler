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
#parameters = pika.ConnectionParameters("localhost")
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
                categoryList, product_info = get_info_from_crawler(url, merchantName) #暂时抓img_url, price, category信息 sku_id已知
            except:
                status = 23 #严重bug, 抓取页面失败
                return status
            productId = self.insert_into_products(product_info[0], product_info[1], product_info[2], url, merchantId, sku_id)
            #获取category_id
            try:
                category_id = None #不知道这一行可不可以省略
                category_id = self.get_category_id_from_categoryList(categoryList, merchantId)
            except:
                status = status * 91 #这个异常是可以跳过
            self.update_category_id(productId, category_id)
            product_info.insert(1, category_id) #增加category_id字段
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
            #新插入的需要增加category_path
            self.update_category_path(productId, detail_info[1])
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
    
    def get_category_id_from_categoryList(self, aList, merchant_id):
        sql1 = """select id from categories where merchant_id=%s and name=%s and parent_id=%s and level=%s"""
        sql2 = """insert into categories(name, merchant_id, parent_id, level) values (%s, %s, %s, %s)"""
        sql3 = """update categories set level1_category_id=%s where id=%s"""
        if not aList:
            return None
        if len(aList) > 0:
            self.db.cursor.execute(sql1, (merchant_id, aList[0], 0, 1))
            result = self.db.cursor.fetchone()
            if result:
                level1 = result[0]
            else:
                self.db.cursor.execute(sql2, (aList[0], merchant_id, 0, 1))
                self.db.cursor.execute(sql1, (merchant_id, aList[0], 0, 1)) #再执行一遍
                level1 = self.db.cursor.fetchone()[0]
                self.db.cursor.execute(sql3, (level1, level1))
        if len(aList) > 1:
            self.db.cursor.execute(sql1, (merchant_id, aList[1], level1, 2))
            result = self.db.cursor.fetchone()
            if result:
                level2 = result[0]
            else:
                self.db.cursor.execute(sql2, (aList[1], merchant_id, level1, 2))
                self.db.cursor.execute(sql1, (merchant_id, aList[1], level1, 2)) #再执行一遍
                level2 = self.db.cursor.fetchone()[0]
                self.db.cursor.execute(sql3, (level1, level2))
        if len(aList) > 2:
            self.db.cursor.execute(sql1, (merchant_id, aList[2], level2, 3))
            result = self.db.cursor.fetchone()
            if result:
                level3 = result[0]
            else:
                self.db.cursor.execute(sql2, (aList[2], merchant_id, level2, 3))
                self.db.cursor.execute(sql1, (merchant_id, aList[2], level2, 3)) #再执行一遍
                level3 = self.db.cursor.fetchone()[0]
                self.db.cursor.execute(sql3, (level1, level3))
        if len(aList) == 3:
            return level3
        elif len(aList) == 2:
            return level2
        else:
            return level1
            
    def update_category_id(self, productId, category_id):
        sql = """update products set category_id=%s where id=%s"""
        if category_id:
            self.db.cursor.execute(sql, (category_id, productId))

    def check_in_product_scores(self, productId):
        sql = """select product_id from product_scores where product_id=%s"""
        self.db.cursor.execute(sql, productId)
        try:
            result = self.db.cursor.fetchone()[0]
        except:
            result = None
        return True if result else False      
                                                            
    def insert_into_product_scores(self, product_info_list):
        #product_info_list: [name, category_id, price, img_url, merchantId, productId, url]
        day = datetime.date.today().strftime("%Y-%m-%d")
        sql = """insert into product_scores (product_name, category_id, price, img_url, merchant_id, product_id, product_url, ct_status, score, calc_date, score_type) values (%s, %s, %s, %s, %s, %s, %s, 4, 0.08, %s, 'HUMAN_SET')"""
        product_info_list[2] = float(extractNum(product_info_list[2])) #scores表中price是double
        product_info_list.append(day)
        self.db.cursor.execute(sql, product_info_list)
    
    def update_category_path(self, productId, category_id):
        if not category_id:
            return ''
        categoryNames = []
        sql="""select parent_id, name from categories where id=%s"""
        current_id = category_id
        while True:
            self.db.cursor.execute(sql, current_id)
            parent_id, name = self.db.cursor.fetchone()
            categoryNames.insert(0, name)
            current_id = parent_id
            if parent_id==0:
                break
        category_path = ' > '.join(categoryNames)
        #执行更新
        sql2 = """update product_scores set category_path=%s where product_id=%s"""
        self.db.cursor.execute(sql2, (category_path, productId))

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
    processer.process(["123456", "http://www.everbuying.net/product1131393.html"])

# test()

def process(info):
    """
       info: 包含 litb_id 和 竞争对手  url
    """
    #每一次调用Java接口, 开关一次数据库连接
    if info=='start':
        processer.db = Db()
        return "Get the cmd to open db..."
    if info=='end':
        processer.db.connect.close()
        return 'Get the cmd to close db...'
    #常规数据
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

#每条记录开关一次数据库的代价太大, 不可以
#     processer.db = Db()

    print(" [.] process(%s)" % body)

    response = process(body)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)
    
#     processer.db.close()
#     processer.db.connect.close()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='auto_crawl')

print(" [x] Awaiting <litb product id> and <competitor's product url> to come...")
channel.start_consuming()