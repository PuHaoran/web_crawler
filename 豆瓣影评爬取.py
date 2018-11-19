#! usr/bin/env python3
# coding='utf-8'
# Author: tudou

import argparse
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import time
import pandas as pd
import getpass

parser=argparse.ArgumentParser()
parser.add_argument('--file',default=None,help='保存的文件名')

def get_login_data():

    user=input("please input your account:")
    passwd=getpass.getpass("please input your passwd: ")

    return user,passwd

def get_html(url,user,password):

    loginurl = 'https://www.douban.com/login?source=movie'

    browser=Chrome()
    browser.get(loginurl)
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel MacOS X 10_13_3) '
                      'AppleWebKit/537.36(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    input=browser.find_element_by_id('email')
    # 控制台输入密码
    passwd=browser.find_element_by_id('password')
    input.send_keys(user)
    passwd.send_keys(password)
    button=browser.find_element_by_name('login')
    # 延时登陆，可以通过手动输入验证码的形式模拟登陆
    time.sleep(5)
    button.click()

    browser.get(url)
    return browser

def get_comment(url,user,password,file=None):

    def store(dic,key,value):
        if value:
            dic.setdefault(key,[]).append(value)
        else:
            dic.setdefault(key,[]).append(0)

    i=1
    browser=get_html(url,user,password)
    data={}
    while True:

        if i==26:
            break
        soup = BeautifulSoup(browser.page_source, 'lxml')
        comments = soup.find_all(class_='comment-item')

        for comment in comments:
            try:
                store(data,'name',comment.select('a')[0].attrs['title'].strip())
                vote_info = comment.select('.comment-vote')[0]
                store(data,'votes',vote_info.select('.votes')[0].text.strip())
                store(data,'title',comment.select('.rating')[0].attrs['title'].strip())
                store(data,'short',comment.select('.short')[0].text.strip())
            except:
                pass

        if i==1:
            browser.find_element_by_css_selector('#paginator a').click()
            i+=1
        else:
            browser.find_element_by_css_selector('#paginator .next').click()
            i+=1
        print('page: {}'.format(i))
        time.sleep(3)
    if file:

        df_data=pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))
        # print(df_data)
        df_data.to_csv(file)
    else:
        print(data)

def test():

    args=parser.parse_args()
    file=args.file
    user,password=get_login_data()
    get_comment('https://movie.douban.com/subject/26636712/comments?start=0&limit=20&sort=new_score&status=P',
                user,password,file)

if __name__ == '__main__':
    test()