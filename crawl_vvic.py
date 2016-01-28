# -*- coding: utf-8 -*-

import httplib2
import pika
import uuid
from pyquery import PyQuery
from utils import clean_html

def load_http_headers(filename):
    headers = {}
    try:
        fr = open(filename, 'r')
        for line in fr:
            fields = line.replace("\n", "").split(": ") #cookie中可能出现':'
            if len(fields) != 2:
                continue
            headers[fields[0]] = fields[1]
    except Exception, e:
        print e
    finally:
        fr.close()
        return headers

def get_config(section, option):
    pass

class Reader:
    pass

class RabbitMQFetcher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        
        self.channel = self.connection.channel()
        
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body #写错self.reponse = body 不出结果
    
#     def call(self, n):
#         self.response = None
#         self.corr_id = str(uuid.uuid4())
#         self.channel.basic_publish(exchange='',
#                                    routing_key='rpc_queue',
#                                    properties=pika.BasicProperties(
#                                     reply_to = self.callback_queue,
#                                     correlation_id = self.corr_id),
#                                    body=str(n))
#         while self.response is None:
#             self.connection.process_data_events()
#         return int(self.response)
    
    def fetch(self, n):
        """n: the n-rd page of www.vvic.com/store.htm
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                  routing_key='rpc_queue',
                                  properties=pika.BasicProperties(
                                    reply_to = self.callback_queue,
                                    correlation_id = self.corr_id),
                                  body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

class Crawler:
    """实现新品信息和图片抓取"""
    
    store_list_page_count = 1
    
    rabbitMQFetcher = RabbitMQFetcher()
    
    def parseProductsBySupplier(self):
        pass
        
    def parseAllSuppliers(self):
        #TODO: 入口信息写入配置文件
#         entrance_page = self.crawlPage("http://www.vvic.com/store.htm")
#         supplierList = self.parseSuppliersPerPage(entrance_page)
#         self.record(supplierList)
        while True:
            if self.store_list_page_count > 500: #做一个低级的限制
                break
            content = self.fetchNextPageConent()
            print content #测试
#             supplierList = self.parseSuppliersPerPage(content)
#             if len(supplierList) == 0:
#                 break
#             else:
#                 self.record(supplierList)
            fw = open("C:/users/chenweiqiang/desktop/cwq" + str(self.store_list_page_count) + '.html', 'w')
            fw.write(content)
            fw.close()
        
    def parseSuppliersPerPage(self, content):
        doc = PyQuery(content)
        supplierNodeList = doc("ul.list-content > li.list-item")
        supplierList = []
        for supplierNode in supplierNodeList:
            supplierNodeQ = PyQuery(supplierNode)
            s = Supplier()
            s.name = supplierNodeQ("li.list-info > h4 > a").text()
            s.url = supplierNodeQ("li.list-info > h4 > a").attr('href')
            s.mainCategory = PyQuery(supplierNodeQ("li.list-info > p").eq(0)).children('span').text()
            s.site = PyQuery(supplierNodeQ("li.list-info > p").eq(1)).children('span').eq(0).text()     
            s.floor = PyQuery(supplierNodeQ("li.list-info > p").eq(1)).children('span').eq(1).text()        
            s.location = PyQuery(supplierNodeQ("li.list-info > p").eq(1)).children('span').eq(2).text()  
            s.city = supplierNodeQ("li.list-place > p > span").eq(0).text()
            s.goodsCount = supplierNodeQ("li.list-count > p.auction-count > span").text()
            s.state = supplierNodeQ("li.list-count > p").eq(-1).text()
            s.description = supplierNodeQ("li.list-place > p > span.remark").text()
            supplierList.append(s)
        return supplierList
    
    def record(self, aList):
        for item in aList:
            print item.name

    def fetchNextPageConent(self):
        content = self.rabbitMQFetcher.fetch(self.store_list_page_count)
        self.store_list_page_count += 1
        return content

    def crawlPage(self, url):
        task = wrap_url(url)
        h = httplib2.Http()
        response, content = h.request(task.url,
                                  method="GET",
                                   headers=task.headers)
        return clean_html(content, task.encoding)
    
    def crawl(self):
        self.parseAllSuppliers()

class FetchTask:
    """用来封装请求信息
    """
    def __init__(self, **kwargs): #传实参的时候是按照关键词参数的形式传的
        self.url = kwargs["url"]
        self.headers = kwargs["headers"]
        self.encoding = kwargs["encoding"]
    
    def to_json(self):
        pass
        
def wrap_url(url):
    return FetchTask(url=url, headers=load_http_headers("./headers/vvic.headers"), encoding="utf-8")  

class Supplier:
    """提供的字段信息:
                 name         店铺名称
                 url          店铺url
                 mainCategory 主营
                 site         商场名
                 floor        楼层
                 location     档口
                 city         城市
                 goodsCount   商品数量
                 state        店铺状态
                 description  可能包含地址和电话,促销信息
    """
    def __init__(self):
        pass

class Saver:
    """将抓完的信息存入数据库, 图片传往S3机器"""
    pass

def run():
    crawler = Crawler()
    crawler.crawl()

if __name__ == '__main__':
#     fibonacci_rpc = RabbitMQFetcher()
#     print " [x] Requesting fib(30)"
#     response = fibonacci_rpc.call(30)
#     print " [.] Got %r" %response
    run()