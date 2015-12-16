from pyquery import PyQuery

class Baokuanyi:
    
    def parseProductsByCategory(self, products_page_content, category_info):
        doc = PyQuery(products_page_content)
        productNodeList = doc('div.shop_items > div[class="col-3-layout ng-scope"]')
        productList = []
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
    
    def parseNextPageUrl(self, products_page_content):
        pass
        