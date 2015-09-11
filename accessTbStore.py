#https://item.taobao.com/item.htm?spm=a230r.1.14.1.JnEHeZ&id=520989811120&ns=1&abbucket=5#detail
import httplib2
import os
import time

def main():
    #httplib2.ServerNotFoundError: Unable to find the server at item.taobao.com
    h = httplib2.Http()
    url = "https://item.taobao.com/item.htm?spm=a230r.1.14.1.JnEHeZ&id=520989811120&ns=1&abbucket=5#detail"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"}
    reponse, content = h.request(url, method="GET", headers=headers)
    print reponse.status
    record_file(content)


def record_file(content, path="C:/users/administrator/desktop", filename="taobao.html"):
    fw = open(os.path.join(path,filename), 'w')
    fw.write(content)
    fw.close()
    
if __name__ == "__main__":
    count = 0 
    while True:
        main()
        print 'sleep...'
        time.sleep(20*60) #20分钟访问一次
        count = count + 1
        if count > 4:
            break
    print 'over...'
