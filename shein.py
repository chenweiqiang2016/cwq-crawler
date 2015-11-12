# -*- coding: utf-8 -*-
from crawler2 import Parser
from pyquery import PyQuery

'''忽略品类 WAHT's NEW, STYLE GALLERY
'''
class SheinParser(Parser):
    current_category = None
    page_idx = 1
    num_idx = 0
    def createCategory(self, menuQ):
        categoryInfo = self.newCategory()
        categoryInfo.name = menuQ.text().strip()
        categoryInfo.url = menuQ.attr('href')
        return categoryInfo.formalize()
    
    def parseCategories(self, homepage_content):
        '''从首页直接解析出全部品类路径
           TOPS, BOTTOMS可以获取至三级品类 其余一级品类获取至二级品类
        '''
        doc = PyQuery(homepage_content)
        categoryList = []
        level1NodeList = doc('ul#TS_menu > li.subCatName')
        for level1Node in level1NodeList:
            level1NodeQ = PyQuery(level1Node)
            level1CateName = level1NodeQ.children('a').text().strip()
            if level1CateName == "WHAT'S NEW" or level1CateName == "Style Gallery":
                continue
            ####################################################################################################
            if level1CateName.upper() == 'DRESSES':
                level2NodeList = level1NodeQ.children('div.Second_ca > ul.loop_ul > li > div').find('li > a') # 1个li下多个div
                for level2Node in level2NodeList:
                    categoryInfo = self.createCategory(PyQuery(level2Node))
                    categoryInfo.parent_categories = [level1CateName]
                    categoryList.append(categoryInfo)
                continue
            ####################################################################################################        
            colNodeList = level1NodeQ.children('div.Second_ca > ul') #ul.loop_ul将SALE品类
            for colNode in colNodeList:
                level2NodeList = PyQuery(colNode).children('li')
                for level2Node in level2NodeList:
                    level2NodeQ = PyQuery(level2Node)
                    if level2NodeQ.children('div'): #这个判断就是: 是否存在三级品类
                        level2CateName = level2NodeQ.children('a').text()
                        level3NodeList = level2NodeQ.children('div').find('li > a')
                        for level3Node in level3NodeList:
                            categoryInfo = self.createCategory(PyQuery(level3Node))
                            categoryInfo.parent_categories = [level1CateName, level2CateName]
                            categoryList.append(categoryInfo)
                    else:
                        categoryInfo = self.createCategory(PyQuery(level2NodeQ.children('a')))
                        categoryInfo.parent_categories = [level1CateName]
                        categoryList.append(categoryInfo)  
        return categoryList
    
    def parseProductsByCategory(self, category_page_content, category_info):
        self.num_idx = 0
        if self.current_category == category_info:
            self.page_idx = self.page_idx + 1
        else:
            self.current_category = category_info
            self.page_idx = 1
        doc = PyQuery(category_page_content)
        productNodeList = doc('div#productsContent1_goods > div')
        productList = []
        for productNode in productNodeList:
            productNodeQ = PyQuery(productNode)
            self.num_idx = self.num_idx + 1
            productInfo = self.newProduct()
            productInfo['sku_id'] = productNodeQ.attr('alt1')
            productInfo['name'] = productNodeQ('div.goods_mz > a').text().strip()
            productInfo['product_url'] = productNodeQ('div.goods_mz > a').attr('href')
            productInfo['img_url'] = productNodeQ('div.goods_aImg > a > img').attr('src')
            productInfo['price'] = productNodeQ('div#cat-product-list_USD > span.special_price').attr('price')
            productInfo['original_price'] = productNodeQ('div#cat-product-list_USD > span.shop_price').attr('price')
            productInfo['page_idx'] = str(self.page_idx)
            productInfo['num_idx'] = str(self.num_idx)
            productInfo.set_categories(category_info)
            productList.append(productInfo)
        return productList

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        aNodeList = doc('div.pageNav > div.pagecurrents2 > a')
        for aNode in aNodeList:
            aNodeQ = PyQuery(aNode)
            if aNodeQ.text().strip().upper() == 'Next':
                url = aNodeQ.attr('href')
                return url
    
    def needProductDetails(self):
        return True
    
    def parseProductDetails(self, product_page_content, product_info):
        doc = PyQuery(product_page_content)
        product_info['reviews'] = doc('a.Rating_div > b').text()
#         product_info['facebook_likes'] = doc('span#u_0_2 > span.pluginCountTextDisconnected').text().strip()
#         product_info['tweet_share'] = doc('div#c > a#count').text().strip()
        product_info['likes'] = self.crawler.fetchSocialLikes(product_info['product_url'])
        imgNodeList = doc('div.other_Imgs > a > div.otheImg_li > img') #div.otheImg_li下存在2个img(重复)
        urls = []
        for imgNode in imgNodeList:
            imgNodeQ = PyQuery(imgNode)
            if imgNodeQ.attr('bigimg'):
                urls.append(imgNodeQ.attr('bigimg'))
        product_info['img_urls'] = ', '.join(urls)
        
    
    