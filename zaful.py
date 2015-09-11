# -*- coding: utf-8 -*-


from pyquery import PyQuery as pq
from crawler2 import Parser
import re
from utils import extractNum

class ZafulParser(Parser):
    crawling_category = {} #只存储正在抓的品类
    def createCategory(self, menuQ):
        categoryInfo = self.newCategory()
        categoryInfo.name = menuQ.text()
        categoryInfo.url = menuQ.attr('href')
        return categoryInfo.formalize()

    def parseCategories(self, homepage_content):
        doc = pq(homepage_content)
        categoryList = []
        level1NodeList = doc('nav#nav > ul > li')
        for level1Node in level1NodeList:
            level1NodeQ = pq(level1Node)
            #一级品类
            if not level1NodeQ.children('div.sub_menu'):
                categoryList.append(self.createCategory(level1NodeQ.children('a')))
                continue
            level1CateName = level1NodeQ.children('a').text().strip()
            level2NodeList = level1NodeQ.children('div.sub_menu > div.fl').find('dl')
            #二级品类
            if len(level2NodeList) == 1:
                for level2Node in pq(level2NodeList).children('dd > a'):
                    categoryInfo = self.createCategory(pq(level2Node))
                    categoryInfo.parent_categories = [level1CateName]
                    categoryList.append(categoryInfo)
            #三级品类
            else:
                #重新定义了level2NodeList 多加了一层限制div.textItem
                for level2Node in level1NodeQ.children('div.sub_menu > div.fl > div.textItem > dl'): #level2NodeList
                    level2CateName = pq(level2Node).children('dt > a').text().strip()
                    level3NodeList = pq(level2Node).children('dd > a')
                    for level3Node in level3NodeList:
                        categoryInfo = self.createCategory(pq(level3Node))
                        categoryInfo.parent_categories = [level1CateName, level2CateName]
                        categoryList.append(categoryInfo)
        return categoryList

    def parseProductsByCategory(self, category_page_content, category_info):
        if not self.crawling_category.has_key(category_info):
            self.crawling_category = {} #清空
            self.crawling_category[category_info] = [1, 0] #开始抓该品类的第一页的商品,已抓商品总计0个
        else:
            self.crawling_category[category_info][0] = self.crawling_category[category_info][0] + 1
        doc = pq(category_page_content)
        productList = []
        if category_info.getLevel1CategoryName() == 'TRENDS':
            nodeList = doc('ul.clearfix > li')
            for i, node in enumerate(nodeList):
                nodeQ = pq(node)
                productInfo = self.newProduct()
                productInfo.set_categories(category_info)
                productInfo['name'] = nodeQ.children('p.goods_title > a').text()
                if not productInfo['name']:
                    productInfo['name'] = nodeQ.children('p.name > a').text()
                productInfo['product_url'] = nodeQ.children('p.goods_title > a').attr('href')
                if not productInfo['product_url']:
                    productInfo['product_url'] = nodeQ.children('p.name > a').attr('href')
                productInfo['img_url'] = nodeQ.children('p.goods_img > a > img').attr('src')
                if not productInfo['img_url']:
                    productInfo['img_url'] = nodeQ.children('p.img > a > img').attr('src')
                productInfo['price'] = nodeQ('p.goods_price > span.shop_price > b.my_shop_price').text()
                if not productInfo['price']:
                    productInfo['price'] = nodeQ('p.was > span.my_shop_price').text()
                if nodeQ('p.goods_price > del.market_price > b.my_shop_price'):
                    productInfo['original_price'] = nodeQ('p.goods_price > del.market_price > b.my_shop_price').text()
                elif nodeQ('p.was > span.market_price > span.my_shop_price'):
                    productInfo['original_price'] = nodeQ('p.was > span.market_price > span.my_shop_price').text()
                else:
                    productInfo['original_price'] = productInfo['price']
                productInfo['sku_id'] = re.findall('p_([\d]+)\.html', productInfo['product_url'])[0]
                productInfo['page_idx'] = str(self.crawling_category[category_info][0])
                productInfo['num_idx'] = str(i + 1)
                productInfo['cate_idx'] = str(self.crawling_category[category_info][1] + 1)
                self.crawling_category[category_info][1] = self.crawling_category[category_info][1] + 1 #每抓一个商品, 加1
                productList.append(productInfo)              
        else:       
            nodeList = doc('div#js_proList > ul > li')
            for i, node in enumerate(nodeList):
                nodeQ = pq(node)
                productInfo = self.newProduct()
                productInfo.set_categories(category_info)
                productInfo['name'] = nodeQ('p.pro_name > a').text().strip()
                productInfo['product_url'] = nodeQ('p.pro_name > a').attr('href')
                productInfo['img_url'] = nodeQ('p.pr > a.pic > img').attr('data-original')
                productInfo['sku_id'] = re.findall('p_([\d]+)\.html', productInfo['product_url'])[0]
                productInfo['price'] = nodeQ.children('p.pro_price > strong.my_shop_price').text()
                if nodeQ.children('p.pro_price > i.costPrice > strong.my_shop_price'):
                    productInfo['original_price'] = nodeQ.children('p.pro_price > i.costPrice > strong.my_shop_price').text()
                else:
                    productInfo['original_price'] = productInfo['price']
                productInfo['page_idx'] = str(self.crawling_category[category_info][0])
                productInfo['num_idx'] = str(i + 1)
                productInfo['cate_idx'] = str(self.crawling_category[category_info][1] + 1)
                self.crawling_category[category_info][1] = self.crawling_category[category_info][1] + 1 #每抓一个商品, 加1
                productList.append(productInfo)
        return productList
    
    def productMixedWithCategory(self):
        return True
        
    def parseProductsAndCategoriesByCategory(self, content, category_info):
        productList, categoryList = [], []
        doc = pq(content)
        # 'NEW ARRIVALS'经过一次处理之后
        if category_info.parent_categories and len(category_info.parent_categories) == 2:
            productList = self.parseProductsByCategory(content, category_info)
            return productList, categoryList
        #SHOP品类已经从首页获取值三级, 品类页面部分还存在四级, 直接忽略
        #TRENDS品类从首页获取到二级品类, 也只有二级品类, 直接抓商品
        if category_info.getLevel1CategoryName() == 'SHOP' or category_info.getLevel1CategoryName() == 'TRENDS':
            productList = self.parseProductsByCategory(content, category_info)
        if category_info.getLevel1CategoryName() == 'NEW ARRIVALS': #首页已获取至二级品类
            nodeList = doc('ul.cataUl_list > li > div.menuList > dl > dt > a')
            for node in nodeList:
                categoryInfo = self.createCategory(pq(node))
                categoryInfo.parent_categories = [category_info.parent_categories[0], category_info.name]
                categoryList.append(categoryInfo)
        if category_info.getLevel1CategoryName() == 'SALE' and category_info.getCurrentLevel()==1: #首页只获取了一级品类名
            level2CategoryList = []
            level2CategoriesPage = self.crawler.fetchCategoryPageContent(category_info.url)
            level2NodeList = pq(level2CategoriesPage)('ul.cataUl_list > li > div.menu > a')
            for node in level2NodeList:
                categoryInfo = self.createCategory(pq(node))
                categoryInfo.parent_categories = ['SALE']
                level2CategoryList.append(categoryInfo)
            for category in level2CategoryList:
                level3CategoriesPage = self.crawler.fetchCategoryPageContent(category.url)
                level3NodeList = pq(level3CategoriesPage)('ul.cataUl_list > li.cur > div.menuList > dl > dt > a')
                if not level3NodeList:
                    categoryList.append(category)
                    continue
                for node in level3NodeList:
                    categoryInfo = self.createCategory(pq(node))
                    categoryInfo.parent_categories = ['SALE', category.name]
                    categoryList.append(categoryInfo)
        return productList, categoryList
    
    def needProductDetails(self):
        return True

    def parseProductDetails(self, product_page_content, product_info):
        doc = pq(product_page_content)
        #http://www.zaful.com/spaghetti-strap-solid-color-openwork-romper-p_45934.html
        if doc('div[class="text_box last_box"] > div.text_tit > strong').text().strip().lower() == 'reviews':
            if doc('div[class="text_box last_box"] > div.text_tit > p.rating > span').eq(1).text():
                product_info['reviews'] = extractNum(doc('div[class="text_box last_box"] > div.text_tit > p.rating > span').eq(1).text())
        product_info['likes'] = self.crawler.fetchSocialLikes(product_info['product_url'])
        imgNodeList = doc('ul.js_scrollableDiv > li.thumbnail_list > a > img')
        imgList = []
        for node in  imgNodeList:
            if pq(node).attr('bigimg'):
                imgList.append(pq(node).attr('bigimg'))
        product_info['img_urls'] = ', '.join(imgList)
        
    def parseNextPageUrl(self, category_page_content):
        doc = pq(category_page_content)
        nodeList = doc('div.bpage > p.listspan > a') #有链接的是<a>元素 没有链接的是<span>元素
        if not nodeList:
            nodeList = doc('div.bpage > p.listspan > span > a')
        for node in nodeList:
            if pq(node).text().strip() == '>':
                url = self.merchant.filteruri(pq(node).attr('href'))
        if locals().has_key('url'): #如果存在url这个变量
            return url
            