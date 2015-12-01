# -*- coding: utf-8 -*-

import re
import ConfigParser

def read_config(filename):
    cf = ConfigParser.ConfigParser()
    cf.read(filename)
    return cf

def read_headers(filename):
    return {}

def extractNum(strText):
    '''仅仅用于对一个数字有关的字符串进行匹配, 多个数字的提取不适用
    '''
    if not strText:
        return 0;
    results = re.findall('[\d, \.]+', strText) #匹配数字
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
        if len(fields) != 2:
            print 'Invalid line: %s' %line
        headers[fields[0].strip()] = fields[1].strip()
    return headers

def getExchangeRate(origin, dest):
    pass
    

if __name__ == '__main__':
    print extractNum('cwq7. 23')
    print extractNum('9,999')
    print extractNum('10.abc')