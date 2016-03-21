# -*- coding: utf-8 -*-

import httplib2
from pyquery import PyQuery

headers = {"Host": "weibo.com", "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Referer": "http://d.weibo.com/102803?topnav=1&mod=logo&wvr=6", "Cookie": "SUB=_2A25778txDeTxGeRP7lAR9SjJzzyIHXVYnLu5rDV8PUNbuNAMLRj3kW9LHeuEYP_viYzCAmHWtacp4QNJynZ9Iw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh95.WncTZQ8V5vSrML9sNn5JpX5K2t; UOR=sports.sina.com.cn,widget.weibo.com,www.baidu.com; SINAGLOBAL=5051435662024.692.1456911150056; ULV=1458289534039:9:9:4:431457533797.8399.1458289534036:1458276213936; login_sid_t=6a9eed32c9f3c0cfafaebf7332df9a9a; YF-Ugrow-G0=ea90f703b7694b74b62d38420b5273df; YF-Page-G0=ed0857c4c190a2e149fc966e43aaf725; _s_tentry=www.baidu.com; Apache=431457533797.8399.1458289534036; SUS=SID-2152056540-1458289441-JA-jt8qv-7ddd8a2b046b4317fd4820a9701a9812; SUE=es%3D990c263093fa6610fc55d4d302f4866e%26ev%3Dv1%26es2%3Daa9019b70a087a25640734a41b2cf7ed%26rs0%3DvGuzjJz3AZBfQs1A8BwNS3qDchWu%252F3q%252FNCq9yllN6F3UKjuzPEDyDhDlDNvvUz0z3G%252B0NvaixOIt5cRcTBZgh%252FkN7kPYhxZgsZSlp6K6XYILbiupDv%252BQmuTGcWHOATmrDvP6mTWZHCyd5tHqjF2Mty%252BE9vZSn5KiecWSk6zEtMk%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1458289441%26et%3D1458375841%26d%3Dc909%26i%3D9812%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D2152056540%26name%3D745926040%2540qq.com%26nick%3D%25E9%259C%2584%25E7%25A5%258E%26fmp%3D%26lcp%3D; SUHB=0gHzlFygKB0YPj; ALF=1489825440; SSOLoginState=1458289441; un=745926040@qq.com; wvr=6; YF-V5-G0=b8115b96b42d4782ab3a2201c5eba25d; wb_publish_vip_2152056540=2; wb_feed_unfolded_2152056540=1", "Connection": "keep-alive"}

def fetch_page_content(url):
    h = httplib2.Http()
    response, content = h.request(url, method="GET", headers=headers)
    return content


if __name__=='__main__':
    content = fetch_page_content("http://weibo.com/guoailun12?refer_flag=1028035010_&is_hot=1")
    doc = PyQuery(content)
    print doc('div[mid="3954100301156805"]').text()
