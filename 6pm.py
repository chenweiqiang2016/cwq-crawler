from crawler2 import Parser
from pyquery import PyQuery

class SixpmParser(Parser):
    
    def parseCategories(self, homepage_content):
        category_info = self.newCategory()
        category_info.name = 'Women'
        category_info.parent_categories = ['Shoes']
        category_info.url = 'http://www.6pm.com/womens-shoes~b?s=goliveRecentSalesStyle/desc/'
        return [category_info]
    
    def parseProductsByCategory(self, category_page_content, category_info):
        doc = PyQuery(category_page_content)
        productNodeList, nodeList = [], doc('div#searchResults > a.product')
        for node in nodeList:
            nodeQ, productInfo = PyQuery(node), self.newProduct()
            productInfo['name'] = nodeQ('span.brandName').text() + ' - ' + nodeQ('span.productName').text()
            productInfo['product_url'] = self.merchant.filteruri(nodeQ.attr('href'))
            productInfo['sku_id'] = nodeQ.attr('data-product-id')
            productInfo['price'] = nodeQ('span.price-6pm').text()
            productInfo['img_url'] = nodeQ('img.productImg').attr('src')
            productInfo['reviews'] = self.crawler.fetcher.fetchSocialLikes(productInfo['product_url'])
            productInfo.set_categories(category_info)
            productNodeList.append(productInfo)
        return productNodeList
    
    def needProductDetails(self):
        return False

    def parseProductDetails(self, product_page_content, product_info):
        pass

    def parseNextPageUrl(self, category_page_content):
        doc = PyQuery(category_page_content)
        if doc('div.pagination > a.arrow:last').attr('href'):
            return self.merchant.filteruri(doc('div.pagination > a.arrow:last').attr('href'))
