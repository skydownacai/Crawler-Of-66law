import os
import requests
from bs4 import BeautifulSoup
import xlwt
import hashlib
import pandas as pd
import base64
from PIL import Image as PILImage
import time
import json
import threading
import traceback
import itertools
import logging
count = 1

def TimeStamp(TIME,timeShuff = False):
    '''返回时间字符串的时间戳
       timeShuff:时间字符串是否包含 时分秒
    '''
    if timeShuff:
        return int(time.mktime(time.strptime(str(TIME),'%Y-%m-%d %H:%M:%S')))
    else:
        return int(time.mktime(time.strptime(str(TIME)+' 08:00:00','%Y-%m-%d %H:%M:%S')))
def md5(strs):
    '这个函数用来计算字符串的md5值'
    m = hashlib.md5()
    m.update(strs.encode('utf-8'))
    return m.hexdigest()
def MkDir(path):
    '''创建目录，如果目录存在就不创建'''
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False
def download_pic(src,path):
    '这个函数用于下载网址为src,保存路径为path的文件'
    r = requests.get(src).content
    with open(path,'wb') as f:
        f.write(r)
def show_pic(path):
    '根据路径显示图片'
    IM = PILImage.open(path)
    IM.show()
def write_category(category,data,page,year,month):
    DATA =xlwt.Workbook()
    sheet = DATA.add_sheet('data')
    keyword = ['时间','问题','问题描述','链接地址','类型','地区','回答人1','回答','赞同数','回答人2','回答','赞同数']
    for i in range(len(keyword)):
        sheet.write(0,i,keyword[i])
    for i in range(len(data)):
        this = data[i]
        for j in range(len(this) - 1):
            sheet.write(i+1,j,this[j])
        for k in range(len(this[-1])):
            sheet.write(i+1,6 + 3*k,this[-1][k][0])
            sheet.write(i+1,7 + 3*k,this[-1][k][1])
            sheet.write(i+1,8 + 3*k,this[-1][k][2])
    MkDir("{}/{}-{}/".format(category,year,month,page))
    DATA.save('{}/{}-{}/{}.xls'.format(category,year,month,page))

def FRatio(x):
    "将小数变为两位百分数"
    y = '%.2f'%float(x * 100)
    return str(y) + "%"
def pass_code(code_name):
        timestamp = str(int(time.time()))
        pdid  = ''                                #------- 在你的网站主页可以看到
        pdkey = ''      #------- 在你的网站主页可以看到
        appid = ''                                #------- 在你的网站主页可以看到+

        appkey= ''      #------- 在你的网站主页可以看到
        sign  =  md5(pdid + timestamp + md5( timestamp + pdkey))
        asign =  md5(appid + timestamp + md5( timestamp + appkey))
        with open(code_name,"rb") as f:
            img_data = base64.b64encode(f.read())
        post_data = {'user_id':"",'timestamp':timestamp,'sign':sign,'asign':asign,"predict_type":"","up_type":"","img_data":img_data}
        #上面是参数准备

        response_platform = json.loads(requests.post('http://pred.fateadm.com/api/capreg',data=post_data).content)
        #print(response_platform)
        #post这个网址进行验证码请求 RetCode":"0"就表明验证请求成功,返回参数为json格式，所以要用json 解析
        raw = response_platform
        code_platform = json.loads(response_platform['RspData'])['result']
        #这句话就获得了平台返回的验证码
        return code_platform
def CheckCustval():
    pdid = '107556'  # ------- 在你的网站主页可以看到
    pdkey = 'dj/XDZSDtN0EMzk8xoZtiinfYu4qRD10'  # ------- 在你的网站主页可以看到
    timestamp = str(int(time.time()))
    sign = md5(pdid + timestamp + md5(timestamp + pdkey))
    post_data = {'user_id': "107556", 'timestamp': timestamp, 'sign': sign}
    responce = json.loads(requests.post("http://pred.fateadm.com/api/custval",data=post_data).text)
    return responce
class crawler:
    def __init__(self,name,tasks):
        self.broswer = requests.session()
        self.count = 1
        self.name = name
        self.proxiesExpire = 0
        self.tasks = tasks
        self.PASS = {
            "page" : []
        }


        self.retry = 0
        self.maxretry = 5
        self.timeout = 20
        self.broswer.keep_alive = False
        print(self.name, ":start!")
    def proxies(self):
        try:
            return self._proxies
        except:
            self._proxies = {
            }
    def delete_pass(self):
        for file in os.listdir():
            if "pass" in file:
                os.remove(file)
    def updateProxies(self):
        api = "http://http.tiqu.qingjuhe.cn/getip?num=1&type=2&pack=36102&port=11&yys=100017&ts=1&lb=1&pb=5&regions=310000,320000"
        while True:
            try:
                raw = json.loads(requests.get(api,timeout=5).text)
            except:
                print('重新获取代理ip重连中')
                time.sleep(2)
                continue
            if raw['msg'] == '请2秒后再试' or len(raw['data']) == 0:
                print(raw)
                print(self.name,'重新获取代理ip重连中')
                time.sleep(2)
                continue
            data = raw['data'][0]
            self.proxiesExpire = TimeStamp(data['expire_time'],timeShuff=True)
            self.proxies = {
                #"http": "http://202.121.96.33:8086",
                "https": "https://{}:{}".format(data['ip'],data['port']),
            }
            print(self.name+' update proxies:'+str(self.proxies["https"]),' ExpiredTime',self.proxiesExpire)
            break
    def ScrapyReply(self,url):
        self.retry = 0
        while True:
            try:
                source = BeautifulSoup(self.broswer.get(url,proxies = self.proxies,timeout = self.timeout).text, 'html.parser')
                break
            except:
                if self.retry == self.maxretry:
                    raise TimeoutError("赞同网页连接超时跳过")
                print('赞同网页掉线,重联中..')
                self.retry += 1
                continue
        Replys = source.find_all(attrs={"class": "reply-list"})
        REPLY = []
        for replys in Replys:
            names = replys.find_all(attrs={"class": 'name'})
            answe = replys.find_all(attrs={'class': 'b'})
            parent = replys.find_all(attrs={'class': 'lh28'})
            for i in range(len(names)):
                zan = parent[i].find(attrs={'class': 's-cb'})
                REPLY.append([names[i].text, answe[i].text, zan.text.split(" ")[0]])
        return REPLY
    def run(self,year,month):
        global count
        broswer = self.broswer
        ALL_data = {'债权债务': []}
        while True:
            if self.page == self.endpage:
                break
            print(self.name,'爬取{}年{}月{}页'.format(year, month, self.page))
            if int(time.time()) >= self.proxiesExpire - 60:
                print(self.name,' proxy:EXPIRED!')
                self.updateProxies()
            self.retry = 0
            while True:
                try:
                    source = broswer.get("http://www.66law.cn/question/{}/{}/{}.aspx".format(year, month, self.page),proxies = self.proxies,timeout = self.timeout)
                    break
                except:
                    print(traceback.format_exc())
                    print(str(self.page) + ':网页加载失败,重联中...')
                    time.sleep(1)
                    if self.retry == self.maxretry:
                        raise TimeoutError("连接超时跳过")
                    self.retry += 1
                    continue
            # source = broswer.get('http://www.66law.cn/waf/aHR0cDovL3d3dy42Nmxhdy5jbjo4MC9xdWVzdGlvbi8yMDE5LzAxLzMuYXNweA==.html?ip=101.94.192.117')
            PAGES = BeautifulSoup(source.text, 'html.parser')
            try:
                items = PAGES.find(attrs={"class": "histroy-art-list"})
                #print(self.name,': ',type(items))
                titles = items.find_all(attrs={"class": 't'})
            except:
                raise ValueError()
                '''
                code_src = 'http://www.66law.cn' + PAGES.find(attrs={"class": "vimg"})['src']
                download_pic(code_src, 'code/{}-{}-{}.png'.format(year, month, self.page))
                code = pass_code('code/{}-{}-{}.png'.format(year, month, self.page))
                print(code, "<{}:{}>".format(self.name,self.count))
                os.rename('code/{}-{}-{}.png'.format(year, month, self.page), "code/{}[{}].png".format(code,int(time.time())))
                requestverficationToken = PAGES.find(attrs={"name": "__RequestVerificationToken"})['value']
                IdentifyId = PAGES.find(attrs={"name": "IdentifyId"})['value']
                Token = PAGES.find(attrs={"name": "Token"})['value']
                ip   = PAGES.find(attrs={"name":"Ip"})['value']
                post_data = {
                    'VerifyCode': code,
                    'Token': Token,
                    'Ip': ip,
                    'IdentifyId': IdentifyId,
                    '__RequestVerificationToken': requestverficationToken
                }
                header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"
                }
                print(header)
                broswer.post('http://www.66law.cn/waf/verify', data=post_data ,headers = header,cookies = broswer.cookies)
                time.sleep(1)
                self.count += 1
                '''
                self.updateProxies()
                continue
            introd = items.find_all(attrs={"class": 'm'})
            inform = items.find_all(attrs={"class": 'b'})
            for i in range(len(titles)):
                raw =titles[i].find('a')
                page_title = raw['title']
                page_url = 'http://www.66law.cn' + raw['href']
                page_int = introd[i].text
                others = inform[i].find_all('span')
                category = others[0].text
                if category not in ALL_data:
                    continue
                location = others[1].text
                TIME = others[2].text
                laywers = others[3].text
                if '无' in laywers:
                    reply = []
                else:
                    reply = self.ScrapyReply(page_url)
                this = [TIME, page_title, page_int, page_url, category, location, reply]
                ALL_data[category].append(this)
            # sum = 0
            # for key in ALL_data:
            #    sum += len(ALL_data[key])
            # print('总条数:{}'.format(sum))
            next_button = PAGES.find(attrs={"class": "u-p-next"})
            if next_button == None:
                break
            else:
                if self.page % 30 == 0:
                    for keyword in ALL_data:
                        write_category(keyword, ALL_data[keyword], int(self.page), year, month)
                        ALL_data[keyword] = []
                self.page += 1
                continue
        for keyword in ALL_data:
            if len(ALL_data[keyword]) != 0:
                write_category(keyword, ALL_data[keyword], 'end'+str(self.page), year, month)
        print(self.name,":done!")
        self.delete_pass()
        pd.DataFrame(self.PASS).to_csv(str(year) + "-" + month +"-"+str(int(time.time())) + '_pass.csv' )
    def scrapy(self):
        for task in self.tasks:
            self.page = task[2]
            year = task[0]
            month = task[1]
            for file in os.listdir():
                if "pass" in file and file.startswith(str(year) +"-"+month):
                    df = pd.read_csv(file)
                    self.PASS['page'] = list(df['page'].values)
            try:
                self.endpage = task[3]
            except:
                self.endpage = 1000000000
            while True:
                try:
                    self.run(year,month)
                    break
                except :
                    self.PASS['page'].append(self.page)
                    self.page += 1
                    self.delete_pass()
                    pd.DataFrame(self.PASS).to_csv(str(year) +"-"+month +"-"+str(int(time.time()))+ '_pass.csv')
                    self.updateProxies()
                    continue

