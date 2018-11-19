#! /usr/bin/env python3
# coding = utf-8
# Author : tudou

import requests
from bs4 import BeautifulSoup
import time
import pymysql
import argparse

parser=argparse.ArgumentParser(prog='houseprice',description='input city')

parser.add_argument('--city','-c',default='bj',help='the city name')
parser.add_argument('--file','-f',help='the file name')
parser.add_argument('--database','-s',default=True,help='save in the database')

#### 获取每个该城市每个区域的链接
def get_areas(city):
    '''
    :param city: 城市
    :return: 返回区域的名称和链接
    '''
    print(">>>>>>>>>>>>>start grabing areas")
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel MacOS X 10_13_3) '
                      'AppleWebKit/537.36(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    url = 'https://%s.lianjia.com/zufang/' %city
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    locate = soup.find(attrs={'data-index': 0})
    areaes = locate.find_all('a')
    areas=[]
    for a in areaes:
        areas.append(a.text)
    links=[]
    for i in range(1,len(areas)):
        base_url=areaes[i].attrs['href']
        area_url='https://%s.lianjia.com' %city+base_url
        links.append(area_url)
    print(">>>>>>>>>>>>areas grap done!")

    return links,areas[1:]

#### 爬取每个区域的房价
def get_pages(link,area,file,choice='txt'):
    '''
    :param link:
    :param area:
    :param file:
    :param choice:存储到txt还是存储到数据库
    :return:
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel MacOS X 10_13_3) '
                      'AppleWebKit/537.36(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    if choice=='db':
        create_database(area,file)
    try:
        for i in range(5):
            url=link+'pg%d' %(i+1)
            rep=requests.get(link,headers=headers).text
            time.sleep(4)
            soup=BeautifulSoup(rep,'lxml')
            items=soup.select('#house-lst')[0].find_all('li')
            if items is None:
                continue
            for item in items:

                item=item.select('.info-panel')[0]
                title=item.find('a').text.strip()
                room=item.select('.zone')[0].text.strip()
                squre=item.select('.meters')[0].text.strip()
                price=item.select('.price .num')[0].text.strip()
                if choice=='txt':
                    with open(file,'a',encoding='utf-8') as f:
                        f.write(area+','+title+','+room+','+squre+','+price+'\n')
                else:
                    data={
                        'title':title.replace(' ',''),
                        'room':room,
                        'squre':squre,
                        'price':price
                    }
                    save_in_database(file,area,data)

            print('>>>>>>>area:{}  page:{} start....'.format(area,i))
        print('>>>>>>>>>>>>area:{} grap done!'.format(area))
    except Exception as e:
        print(e)
        print('ooops! connecting error, retrying.....')

#### 数据库操作
def create_database(area,file):
    db = pymysql.connect(host='localhost', user='tudou', password='123', port=3306)
    cursor = db.cursor()
    cursor.execute('show databases')
    data = cursor.fetchall()
    if file not in data:
        try:
            sql="create database if not exists %s;" % file
            cursor.execute(sql)
            db.commit()
        except:
            print("database create error!")
            db.rollback()

    cursor.execute('use %s;' %file)
    try:
        cursor.execute("create table if not exists %s (id int unsigned primary key auto_increment,title text,room varchar(255),squre varchar(255),price varchar(255));" %area)
        db.commit()

    except Exception as e:
        print(e)
        print("table create error!")
        db.rollback()

    db.close()

def save_in_database(file,area,data):
    db = pymysql.connect(host='localhost', user='tudou', password='123', port=3306,database=file,charset='utf8')
    cursor = db.cursor()

    key=','.join(data.keys())
    value=','.join(len(data)*['%s'])
    sql="insert into {} ({}) values ({});".format(area,key,value)
    cursor.execute(sql,tuple(data.values()))
    db.commit()
    db.close()

def main():

    print('>>>>>>>start webcrawl')

    args=parser.parse_args()
    city=args.city
    file=args.file
    database=args.database
    if database:
        choice='db'
    else:
        choice='txt'
    links,areas=get_areas(city)

    for i,j in zip(links,areas):
        get_pages(i,j,file,choice)

if __name__ == '__main__':
    main()







