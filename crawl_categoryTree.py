# -*- coding: utf-8 -*-

import httplib2
import xlwt
from pyquery import PyQuery

def crawl_1688_category_tree(wb):
    #fr = open("C:users/chenweiqiang/desktop/ye.html", "r") #PyQuery之后取不出来元素
    h = httplib2.Http()
    response, content = h.request("https://ye.1688.com/")
#     fw = open("C:users/chenweiqiang/desktop/ye2.html", "w")
#     fw.write(content)
#     fw.close()
    ws = wb.add_sheet("ye.1688品类树")
    ws.write(0,0,"一级品类")
    ws.write(0,1,"二级品类")
    ws.write(0,2,"三级品类")
    row = 0
    doc = PyQuery(content)
    level1NodeList = doc("li.cat-box")
    for level1Node in level1NodeList:
        level1NodeQ = PyQuery(level1Node)
        level1_category = level1NodeQ('div.cat-main').text().replace(' ', '')
        level2NodeList = level1NodeQ('div.cat-sub-col > dl') # 多余div[class="cat-sub "] > 
        for level2Node in level2NodeList:
            level2NodeQ = PyQuery(level2Node)
            level2_category = level2NodeQ('dt > a').text()
            level3NodeList = level2NodeQ('dd.cat-list > ul > li > a')
            for level3Node in level3NodeList:
                level3NodeQ = PyQuery(level3Node)
                level3_category = level3NodeQ.text()
                row += 1
                ws.write(row, 0, level1_category)
                ws.write(row, 1, level2_category)
                ws.write(row, 2, level3_category)

def crawl_vvic_category_tree(wb):
    h = httplib2.Http()
    response, content = h.request("http://www.vvic.com/")
#     fw = open("C:users/chenweiqiang/desktop/vvic2.html", "w")
#     fw.write(content)
#     fw.close()
    ws = wb.add_sheet("vvic品类树")
    ws.write(0,0,"一级品类")
    ws.write(0,1,"二级品类")
    ws.write(0,2,"三级品类")
    row = 0
    doc = PyQuery(content)
    level1NodeList = doc("div.dd-inner > div.item")
    anotherLevel1NodeList = [doc('div.sub-items')[0], doc('div.sub-items')[1], doc('div.sub-items')[2], doc('div.sub-items')[5]]
    for index, level1Node in enumerate(level1NodeList):
        level1_category = PyQuery(level1Node)('h3 > a').text()
        level2NodeList = PyQuery(anotherLevel1NodeList[index]).children('dl')
        for level2Node in level2NodeList:
            level2NodeQ = PyQuery(level2Node)
            level2_category = level2NodeQ.children('dt > a').text()
            level3NodeList = level2NodeQ.children('dd > a')
            for level3Node in level3NodeList:
                level3_category = PyQuery(level3Node).text()
                row += 1
                ws.write(row, 0, level1_category)
                ws.write(row, 1, level2_category)
                ws.write(row, 2, level3_category)

def crawl():
    wb = xlwt.Workbook(encoding="utf-8")
    crawl_1688_category_tree(wb)
    crawl_vvic_category_tree(wb)
    wb.save("C:users/chenweiqiang/desktop/category_tree.xls")

if __name__ == '__main__':
    crawl()