# -*- coding: utf-8 -*-

"""
        支持的商户有: dx, focalprice
"""
from pyquery import PyQuery
import re
import httplib2

def extract(url):
    #http://www.dx.com/p/h06-multi-function-gms-gps-gprs-vehicle-tracker-black-172624#.VuKnvnqcOjg
    sku_id = ''
    if url.find("dx") > 0:
        sku_id = get_sku(url, "-([\d]+)[#$]")
    #http://www.focalprice.com/ID705W/Genuine_EU_Type_USB_Power_Adapter_for_iPad__iPhone_White.html
    elif url.find("focalprice") > 0:
        sku_id = get_sku(url, "/([\w]+)/")
    #http://www.aliexpress.com/item/2015-Hot-1pc-EU-3-7V-18650-14500-16430-Battery-Charger-For-Rechargeable-Batteries-100-240V/32526656433.html?spm=2114.01010108.3.11.TQxQti&ws_ab_test=searchweb201556_9,searchweb201602_4_505_506_503_504_10034_10020_502_10001_10002_10017_10010_10005_10006_10011_10003_10021_10004_10022_10009_10008_10018_10019,searchweb201603_8&btsid=15e4ae0c-d0ca-408c-8e51-c5ee665c0bd9
    elif url.find("aliexpress") > 0:
        sku_id = get_sku(url, "/(\d+)\.html")
    #http://www.amazon.com/Amazon-PowerFast-Official-Charger-eReaders/dp/B00QFQRELG/ref=sr_1_2?s=fiona-hardware&ie=UTF8&qid=1458026901&sr=1-2
    elif url.find("amazon") > 0:
        sku_id = get_sku(url, 'dp/([\w]+)/')
    #http://www.ebay.com/itm/Sexy-Lace-Long-Chiffon-Evening-Formal-Party-Cocktail-Dress-Bridesmaid-Prom-Gown-/331545169993?var=540703382856&_trkparms=%26rpp_cid%3D5548e85be4b0779e680941cc%26rpp_icid%3D55493ffde4b0969de4ede164
    elif url.find("ebay") > 0:
        sku_id = get_sku(url, '/(\d+)$')
        if not sku_id:
            sku_id = get_sku(url, '/(\d+)[\?]')
    return sku_id

def get_sku(url, pattern):
    if re.findall(pattern, url):
        return re.findall(pattern, url)[0]
    return ''

def extractMerchantName(url):
    if url.find("dx") > 0:
        return "dx"
    elif url.find("focalprice") > 0:
        return "focalprice"
    elif url.find("aliexpress") > 0:
        return "ALI99"
    elif url.find("amazon") > 0:
        return "AMZ99"
    elif url.find("ebay") > 0:
        return "EBY99"
    
def get_info_from_crawler(url, merchantName):
    content = fetch_page_content(url)
    doc = PyQuery(content)
    if merchantName == 'dx':
        name = doc("h1 > span#headline").text()
        price = doc("span#price").text()
        img_url = "http:" + doc("div#midPicBox > a#product-large-image > img").attr("src") if doc("div#midPicBox > a#product-large-image > img").attr("src") else None
    elif merchantName == 'focalprice':
        name = doc("h1#productName").text()
        price = doc("span#unit_price").text()
        img_url = doc("ul#imgs > li > img").eq(0).attr("jqimg")
    elif merchantName == 'ALI99':
        name = doc('h1.product-name').text()
        price = doc("div#product-price").text()
        img_url = doc("div#magnifier > div > a > img").eq(0).attr('src')
    elif merchantName == 'AMZ99':
        name = doc('span#productTitle').text()
        price = doc('span#priceblock_ourprice').text()
        img_url = doc('div#imgTagWrapperId > img#landingImage').attr('data-old-hires')
    elif merchantName == 'EBY99':
        name = doc('h1#itemTitle').remove('span').text()
        price = doc('span#mm-saleDscPrc').text()
        img_url = doc('img#icImg').attr('src')
    return [name, price, img_url]

def fetch_page_content(url):
    h = httplib2.Http()
    response, content = h.request(url)
    if response.status == 200:
        return content
    
#==========================================================================================
#             categoryList = []
#             categoryNodeList = doc("div.wrapper > div.position > a")
#             for node in categoryNodeList:
#                 nodeQ = PyQuery(node)
#                 categoryList.append(nodeQ.text().strip()) if nodeQ.text().strip() else """do nothing"""
