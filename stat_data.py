# -*- coding: utf-8 -*-

import codecs
import StringIO

def ensure_num(value):
    if not value:
        return '0'
    return value.replace(',', '').replace('$', '')

def scale_percent(part, total):
    percent = int(round(part * 100.0 / total)) + 1
    if percent > 100:
        percent = 100
    return percent

class Stat:
    def __init__(self, filename, field=None):
        self.filename = filename
        self.fieldList = []
        if field:
            self.fieldList.append(field)
        self.parseHeaders()
    
    def parseHeaders(self):
        fin = open(self.filename, 'r')
        line = fin.readline()
        self.headers = self.read_headers(line)
        fin.close()
        #初始化
        self.reviewsIndex, self.likesIndex, self.reviewsRadio, self.likesRadio = \
        (-1, -1, 0, 0)
        #这一步可以在init中做
        if not self.fieldList:
            self.fieldList = ['reviews', 'likes']
        if 'reviews' in self.fieldList:
            if 'reviews' in self.headers:
                self.reviewsIndex = self.headers.index('reviews')
                self.reviewsRadio = 1.0
            else:
                self.fieldList.remove('reviews')
        if 'likes' in self.fieldList:
            if 'likes' in self.headers:
                self.likesIndex = self.headers.index('likes')
                self.likesRadio = 1.0
            else:
                self.fieldList.remove('likes')
        #必须确保'reviews'或者'likes'同时存在于self.fieldList和self.headers
        if self.reviewsIndex < 0 and self.likesIndex < 0:
            raise Exception('No scoring fields for file: %s' %self.filename)
        if self.reviewsIndex >=0 and self.likesIndex >= 0: #重新调整reviewsRadio
            self.reviewsRadio = self.calcuReviewsLikesRadio()

    def read_headers(self, line):
        if line.startswith(codecs.BOM_UTF8):
            line = line[len(codecs.BOM_UTF8):]
        fields = line.strip().split('\t')
        return fields
    
    def calcuReviewsLikesRadio(self):
        fin = open(self.filename, 'r')
        fin.readline() #跳过表头
        total_reviews, total_likes = 0, 0
        for line in fin:
            reviews, likes = self.reviewsAndLikesPerRow(line)
            total_reviews += reviews
            total_likes += likes
        fin.close()
        if total_reviews > 0 and total_likes > 0:
            return total_likes * 1.0 / total_reviews
        else:
            return 1.0

    def reviewsAndLikesPerRow(self, line):
        datas = line.split('\t')
        reviews = int(ensure_num(datas[self.reviewsIndex])) if self.reviewsIndex>=0 else 0
        likes = int(ensure_num(datas[self.likesIndex])) if self.likesIndex>=0 else 0
        return (reviews, likes)
    
    def stat(self):
        fin = open(self.filename, 'r')
        fin.readline()
        statDist = {}
        #统计处每一个reviews对应的商品数目, 以及全部商品数目
        totalProductCount = 0
        for line in fin.readlines():
            reviews, likes = self.reviewsAndLikesPerRow(line)
            data = int(round(reviews * self.reviewsRadio + likes * self.likesRadio))
            totalProductCount += 1
            if statDist.has_key(data):
                statDist[data] += 1
            else:
                statDist[data] = 1
        #计算每一个reviews对应已经累计的topCount和topPercent
        statList = []
        topCount = 0
        for reviews in sorted(statDist, reverse=True):
            topCount += statDist[reviews]
            topPercent = scale_percent(topCount, totalProductCount)
            statList.append([reviews, topCount, topPercent])
        #根据topPercent进行汇总
        start_item = statList[0]
        last_item = statList[0]
        finalStatList = []
        for item in statList:
            if item[2] != start_item[2]: #意味着topPercent发生变化
                merge_item = [start_item[0], last_item[0], last_item[1], last_item[2]] #最大reviews 最小reviews 累计的商品数 累计的百分比
                finalStatList.append(merge_item)
                start_item = item
            last_item = item
        finalStatList.append([0, 0, totalProductCount, 100])
        return StatResult(self.getOriginScoringFields(),
                          self.getScoringField(),
                          finalStatList)
    
    def getOriginScoringFields(self):
        return self.fieldList
    
    def getScoringField(self):
        return 'likes' if 'likes' in self.headers else 'reviews'

class StatResult:
    def __init__(self, fields, scoringField, result):
        self.fields = fields
        self.scoringField = scoringField
        self.statResult = result
    
    def output(self):
        output = StringIO.StringIO()
        totalProductCount = self.statResult[-1][2]
        print >> output, 'Use scoring fields: %s' %(self.fields)
        print >> output, 'Find scoring field: %s' %self.scoringField
        for merge_item in self.statResult:
            print >> output, 'Top %3d%% %5d (%3d - %3d %s)' %(merge_item[3], merge_item[2], merge_item[1], merge_item[0], self.scoringField)
        print >> output, '              (total count: %d)' %(totalProductCount)
        return output.getvalue()
    
if __name__ == '__main__':
    s = Stat('focalprice_12-11-2015_productInfo.inprogress')
    result = s.stat()
    print result.output()
    
        
            
        
        