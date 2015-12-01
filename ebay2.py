import re
from pyquery import PyQuery
from utils import extractNum

class EbayParser():
    def extractSkuId(self, url):
        #http://www.ebay.com/itm/SDS-P4042-Samsung-8ch-960H-Security-Camera-System-500GB-4-Night-Cameras-/291533443868?hash=item43e0bf531c:g:3RwAAOSwgQ9V4LDN
        if re.findall("/([\d]+)\?", url):
            return re.findall("/([\d]+)\?", url)[0]
        
    
    def parseProducts(self, product_page_content, category_info):
        doc = PyQuery(product_page_content)
        productNodeList = doc("")
        for node in productNodeList:
            nodeQ = PyQuery(node)
            productInfo = self.newProduct()
        #<span class="bold">
                    #<b>HKD</b> 635.43</span>
        #有可能在span之前
        #<div class="medprc">
                                    #<span class="prcVS">Trending at</span>
                                    #<span class="median">HKD 3,712.29<a id="medianPrcHelp_e1-115" class="sh-qmark" href="javascript:;"></a></span>
                                #</div>
            productInfo['price'] = nodeQ('ul.lvprices > li[class="lvprice prc"] > span.bold').remove('div.medprc').text()

    def processPrice(self, price):
        if price.startswith("HKD"):
            price = extractNum(price)
            return str(round((float(price) / 7.750200), 2))

class EbayStoreParser():
    pass
