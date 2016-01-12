from pyquery import PyQuery

class JollychicParser:

    def parseCategories(self, homepage_content):
        categoryList = []
        doc = PyQuery(homepage_content)
        level1NodeList = doc('ul[class="header-nav fn-clear J-nav-list"] > li')
        for index, level1Node in enumerate(level1NodeList):
            level1NodeQ = PyQuery(level1Node)
            level1Name = level1NodeQ.children('a').text()
            innerNodeList = level1NodeQ.children('div.catagory-block > dl > dd')
            for index2, innerNode in enumerate(innerNodeList):
                innerNodeQ = PyQuery(innerNode)
                if innerNodeQ.attr('class') == 'fn-bold':
                    level2CateName = None
                    if index2 == len(innerNodeList) - 1 or PyQuery(innerNodeList[index+1]).attr('class') == 'fn-bold': #最后一个节点加黑 直接是没有三级品类的二级品类
                        categoryInfo = self.createCategory(innerNodeQ)
                        categoryInfo.parent_categories = [level1Name]
                        if categoryInfo.name and categoryInfo.url:
                            categoryList.append(categoryInfo)
                    else:
                        level2CateName = innerNodeQ.text()
                else:
                    categoryInfo = self.createCategory(innerNodeQ)
                    if locals().has_key('level2CateName') and level2CateName:
                        categoryInfo.parent_categories = [level1Name, level2CateName]
                    else:
                        categoryInfo.parent_categories = [level1Name]
                    if categoryInfo.name and categoryInfo.url:
                        categoryList.append(categoryInfo)
        return categoryList