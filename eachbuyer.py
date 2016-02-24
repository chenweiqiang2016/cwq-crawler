"""
    2016/02/24 Chen Weiqiang 增加parseProductDetails 部分修改parseProductsByCategory
"""


from pyquery import PyQuery

def parseCategories():
    categoryList = []
    node = doc("ul#categrayAll > li").eq(0) #只抓了第一个一级品类
    nodeQ = PyQuery(node)
    level1Name = nodeQ.children('div.li > a > em').text()
    level2NodeList = nodeQ.children('div.sub-list > div > ul.column > li.level1')
    for level2Node in level2NodeList:
        level2NodeQ = PyQuery(level2Node)
        category = self.newCategory()
        category.name = level2NodeQ.children('a').text()
        category.url = level2NodeQ.children('a').attr("href")
        category.parent_categories = [level1Name]
        categoryList.append(category)
    return categoryList

def parseProductsByCategory():
    #productNodeList = doc('div.primary-list > ul.clearfix > li') 有效, 作用相同
    productNodeList = doc('div.primary-list > ul > li > div.pro-list-block') #48
    for node in productNodeList:
        nodeQ = PyQuery(node)
        product = self.newProduct()
        product['name'] = nodeQ("div.p-name > a").attr('title') #.text()
        product['product_url'] = nodeQ("div.p-name > a").attr('href')
        productInfo['img_url'] = nodeQ('div.p-pic').find('img').attr('src')
        #product['img_url'] = nodeQ("div.p-pic > a > img").attr('data-lazysrc')
        product['price'] = nodeQ('div.p-price > span.p-price-n').text().strip()
        product['price_old'] = nodeQ('div.p-price > span.p-price-o').text().strip()

def parseProductDetails():
    doc('div.discount-price > b > span.salePrice').text()
    