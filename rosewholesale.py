# -*- coding: utf-8 -*-

from pyquery import PyQuery
import re
from utils import extractNum
from crawler2 import Parser
from logging import info

class RosewholesaleParser(Parser):
    crawling_category = {} #只存储正在抓的品类
    def createCategory(self, menuQ):
        categoryInfo = self.newCategory()
        categoryInfo.name = re.sub('\([\d]+\)', '', menuQ.text().strip())
        categoryInfo.url = menuQ.attr('href')
        return categoryInfo

    def parseCategories(self, homepage_content):
        '''从首页最多获取至二级品类
        '''
        doc = PyQuery(homepage_content)
        categoryList = []
        level1NodeList = doc('nav#nav > div.w > ul > li')
        for level1Node in level1NodeList:
            level1NodeQ = PyQuery(level1Node)
            if not level1NodeQ.children('div.sub_menu'):
                categoryInfo = self.createCategory(level1NodeQ.children('a'))
                categoryList.append(categoryInfo)
            else:
                level1Name = level1NodeQ.children('a').text()
                level2NodeList = level1NodeQ.children('div.sub_menu > div.leftWrap > div.leftTitle > dl')
                for level2Node in level2NodeList:
                    level2NodeQ = PyQuery(level2Node)
                    if level2NodeQ.find('dt'): #每个二级品类名会重复出现
                        continue
                    elif level2NodeQ.find('dd'):
                        categoryInfo = self.createCategory(level2NodeQ.children('dd > a'))
                        categoryInfo.parent_categories = [level1Name]
                        categoryList.append(categoryInfo)
        return categoryList

    def parseProductsByCategory(self, category_page_content, category_info):
        if not self.crawling_category.has_key(category_info):
            self.crawling_category = {} #清空
            self.crawling_category[category_info] = [1, 0] #开始抓该品类的第一页的商品,已抓商品总计0个
        else:
            self.crawling_category[category_info][0] = self.crawling_category[category_info][0] + 1
        doc = PyQuery(category_page_content)
        productList = []
        productNodeList = doc('div#js_proList > ul > li')
        for i, productNode in enumerate(productNodeList):
            productNodeQ = PyQuery(productNode)
            productInfo = self.newProduct()
            part1 = productNodeQ.children('p.pr')
            productInfo['img_url'] = PyQuery(part1).children('a.pic > img').attr('data-original')
            part2 = productNodeQ.children('p.pro_name')
            productInfo['name'] = PyQuery(part2).children('a').text().strip()
            productInfo['product_url'] = PyQuery(part2).children('a').attr('href')
            productInfo['sku_id'] = re.findall('-([\d]+)\.html', productInfo['product_url'])[0]
            part3 = productNodeQ.children('p.pro_price')
            productInfo['price'] = PyQuery(part3).find('strong.my_shop_price').text()
            productInfo.set_categories(category_info)
            productInfo['page_idx'] = str(self.crawling_category[category_info][0])
            productInfo['num_idx'] = str(i + 1)
            productInfo['cate_idx'] = str(self.crawling_category[category_info][1] + 1)
            productList.append(productInfo)
            self.crawling_category[category_info][1] = self.crawling_category[category_info][1] + 1 #每抓一个商品, 加1
        info('%s has been crawled %d products after parse %d pages。' %(category_info, self.crawling_category[category_info][1], self.crawling_category[category_info][0]))
        return productList

    def parseProductsAndCategoriesByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productList, categoryList = [], []
        if category_info.parent_categories and len(category_info.parent_categories) == 2:
            productList = self.parseProductsByCategory(category_page_content, category_info)
            return productList, categoryList
        if category_info.name == 'New Arrivals': #特殊处理一下
            for level2Node in doc.find('div#js_catelist_sec > div.item'):
                level2NodeQ = PyQuery(level2Node)
                level2CateName = level2NodeQ.children('p > a').text()
                for level3Node in level2NodeQ.children('ul > li > a'):
                    categoryInfo = self.createCategory(PyQuery(level3Node))
                    categoryInfo.parent_categories = [category_info.name, level2CateName]
                    categoryList.append(categoryInfo.formalize())
            return  productList, categoryList
        if category_info.name == 'Clearance':
            level2NodeList = doc('div.catelist > ul.cataUl_list > li > a')
            for level2Node in level2NodeList:
                categoryInfo = self.createCategory(PyQuery(level2Node))
                categoryInfo.parent_categories = ['Clearance']
                categoryList.append(categoryInfo.formalize())
            return productList, categoryList
        if doc.find('div#js_catelist_sec > div.cur > ul > li'):
            nodeList = doc.find('div#js_catelist_sec > div.cur > ul > li > a')
            for node in nodeList:
                nodeQ = PyQuery(node)
                categoryInfo = self.newCategory()
                categoryInfo.name = nodeQ.text()
                categoryInfo.url = nodeQ.attr('href')
                categoryInfo.set_categories(category_info)
                categoryList.append(categoryInfo.formalize())
        elif doc.find('div.catelist > ul > li.cur > div.menuList > p'):
            nodeList = doc.find('div.catelist > ul > li.cur > div.menuList > p > a')
            for node in nodeList:
                nodeQ = PyQuery(node)
                categoryInfo = self.newCategory()
                categoryInfo.name = nodeQ.text()
                categoryInfo.url = nodeQ.attr('href')
                if  category_info.parent_categories:
                    result = category_info.parent_categories + [category_info.name]
                else:
                    result = [category_info.name]
                categoryInfo.parent_categories = result
                categoryList.append(categoryInfo.formalize())
        else:
            productList = self.parseProductsByCategory(category_page_content, category_info)
        return productList, categoryList
   
    def productMixedWithCategory(self):
        return True
    
    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        nodeList = doc('p.listspan').children('span > a') #debug得到的结果
        if not nodeList:
            nodeList = doc('p.listspan').children('a') #fw保存下来是这种格式
        url = None
        for node in nodeList:
            nodeQ = PyQuery(node)
            if nodeQ.text().strip() == '>':
                url = nodeQ.attr('href')
                break
        if url:
            print self.merchant.filteruri(url)
            return self.merchant.filteruri(url)
    
    def needProductDetails(self):
        return True
    
    def parseProductDetails(self, product_page_content, product_info):
        doc = PyQuery(product_page_content)
        #为js加载, 内容没有成功地获取
        #此处的likes为facebook, twitter等的合计
        #product_info['likes'] = doc('div.addthis_toolbox > a.addthis_counter > a.addthis_button_expanded').text().strip()
        product_info['reviews'] = extractNum(doc('a#js_gotoReviwBlock').text())
        #调用api来获取facebook的likes数目
        try:
            product_info['likes'] = self.crawler.fetchSocialLikes(product_info['product_url'])
        except:
            print 'fetch facebook like failed...' + '@' + 'http://graph.facebook.com/' + product_info['product_url']
            product_info['likes'] = '0'         
        #获取图片url
        product_info['img_urls'] = []
        imageNodeList = doc('div.goodImg_list > ul.slider > li > a > img')
        for imageNode in imageNodeList:
            image_url = PyQuery(imageNode).attr('bigimg')
            if not image_url:
                image_url = PyQuery(imageNode).attr('src')
            if image_url:
                product_info['img_urls'].append(image_url)
        product_info['img_urls'] = ', '.join(product_info['img_urls'])

    def needProductImages(self):
        return True

#     def needSaveImages(self):
#         return True

     
