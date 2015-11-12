from pyquery import PyQuery

class AmazonUrlParser:
    def parseProducts(self, page_content):
        doc = PyQuery(page_content)
        productlist = []
        #url: http://www.amazon.com/s/ref=lp_12597713011_st?lo=fashion&rh=n%3A7141123011%2Cn%3A12597713011&qid=1446089330&sort=review-rank
        #所见doc("div#atfResults > ul#s-results-list-atf > li")并非实际 只找到6个
        #往上走两级div#resultsCol可得到60个
        productNodeList = doc("div#resultsCol").find("li")
        
        
        
        
        #url: http://www.amazon.com/s/ref=sr_pg_1?rh=n%3A7141123011%2Cn%3A11651065011&ie=UTF8&qid=1446715289&lo=fashion&ajr=2
        #第一页是这个
        #第二页同上
        doc("div#search-results > div#mainResults > ul > li")
        return productlist
    
        #url: http://www.amazon.com/b/ref=fs_w_sho_lp_vd2_athletic?_encoding=UTF8&lo=fashion&node=11379260011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-5&pf_rd_r=0D9Y33W84Y6HMRYC7ZC5&pf_rd_t=101&pf_rd_p=2258134242&pf_rd_i=679337011
        #第一页57个 并且有第二页