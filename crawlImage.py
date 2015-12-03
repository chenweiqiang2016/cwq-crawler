
import urllib2
import uuid
import os
import re

def crawl_img(url, saveDir='E:/images', picName=None):
    known_suffix_list = ['jpg']
    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    suffix = re.findall('\.([a-z]+)$', url)[0]
    if suffix not in known_suffix_list:
        print suffix
    if not picName:
        picName = str(uuid.uuid4()) + '.' + suffix
    savePath = os.path.join(saveDir, picName)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0"}
    timeout = 30
    request = urllib2.Request(url, None, headers)
    page = urllib2.urlopen(request, None, timeout)
    content = page.read()
    with open(savePath, 'wb') as img_file:
        img_file.write(content)
        img_file.close()

crawl_img("http://gloimg.sammydress.com/S/2015/201510/source-img/1446074274928-P-3339590.jpg")
crawl_img("http://img.banggood.com/thumb/view/2014/gongsijie/11/SKU109521/SKU10952011.jpg")