# -*- coding: utf-8 -*-

import re
import httplib2
import time
import random
from ConfigParser import ConfigParser

'''此处fetchPageWithUrl使用的是'GBK'解码
'''


class KindConfigParser(ConfigParser):
    def get2(self, option, default=''):
        result = ''
        try:
            result = self.get('default', option)
        except:
            result = default
        return result

def read_config(filename):
    lines = read_file(filename)
    return read_configbytext(lines)

def read_configbytext(lines):
    if not re.findall("\[[\w]+\]", lines):
        lines = '[default]\n' + lines
    fp = open('./config/tmp.cfg', 'w')
    fp.write(lines)
    fp.close()
    config = KindConfigParser()
    config.readfp(open('./config/tmp.cfg', 'r'))
    return config

def read_file(filename):
    fr = open(filename, 'r')
    try:
        return fr.read()
    finally:
        fr.close()

def read_headers(filename):
    return {}

def extractNum(strText):
    '''仅仅用于对一个数字有关的字符串进行匹配, 多个数字的提取不适用
    '''
    if not strText:
        return 0;
    results = re.findall('\d[\d, \.]*', strText) #匹配数字, 前面加一个\d
    if results:
        result = re.sub(',', '', re.sub(' ', '', results[0])) #去除空格和逗号分隔
        if re.findall('[\.]', result): #有小数点的进行浮点数, 没有的话整理成整数
            return float(result)
        else:
            return int(result)
    return 0

def load_http_headers(filename):
    headers = {}
    fr = open(filename, 'r')
    while True:
        line = fr.readline().strip()
        if not line:
            break
        fields = line.split(':')
        if len(fields) > 2: #Invalid line: User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0
            fields = line.split(': ')
        if len(fields) != 2:
            print 'Invalid line: %s' %line
            continue
        headers[fields[0].strip()] = fields[1].strip()
    return headers

def getExchangeRate(origin, dest):
    pass

def print_csvline(fw, datas):
    #['\xe6\x95\xb0\xe7\xa0\x81', '\xe6\x99\xba\xe8\x83\xbd\xe8\xae\xbe\xe5\xa4\x87', u'\u5c0f\u7c73\uff08MI\uff09\u667a\u80fd\u4f53\u91cd\u79e4 \u5bb6\u7528\u5065\u5eb7\u79e4 \u7cbe\u51c6\u79e4', '1545210']
    #UnicodeDecodeError: 'ascii' codec can't decode byte 0xe6 in position 0: ordinal not in range(128)
    for i in range(0, len(datas)):
        if datas[i] is None:
            datas[i] = ''
        if isinstance(datas[i], unicode):
            datas[i] = datas[i].encode('utf-8')
    fw.write('\t'.join(datas) + '\n')

def clean_html(content, decode="utf-8"):
#     content = content.replace("\r\n", "")
    #TODO: 此处需要改进
    content = re.sub('<!DOCTYPE.*dtd">', "", content)
    #这个操作非常关键, 否则PyQuery得不出正确的结果
    content = unicode(content, decode)
    return content

def fetchPageWithUrl(url):
    time.sleep(random.uniform(0, 2))
    h = httplib2.Http()
    response, content = h.request(url)
    if response.status == 200:
        return unicode(content, 'GBK')

if __name__ == '__main__':
    print extractNum('cwq7. 23')
    print extractNum('9,999')
    print extractNum('10.abc')