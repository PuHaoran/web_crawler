#! usr/bin/env python3
# coding='utf-8'
# Author: tudou

import requests
from bs4 import BeautifulSoup
import time
import pymysql
import argparse

parser=argparse.ArgumentParser(description="拉勾网爬虫")
parser.add_argument('--work',required=True,help="想要爬取的工种")
parser.add_argument('--file',help="存储的文件")
parser.add_argument('--db',help='存储到数据库')

def get_page(work,page):
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Host': 'www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90?labelWords=&fromSearch=true&suginput=',
        'X-Anit-Forge-Code': '0',
        'X-Anit-Forge-Token': 'None',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
    data={}
    data['kd']=work
    data['pn'] = page
    if page==1:
        data['first']='true'
    else:
        data['first']='false'

    response=requests.post(url,headers=my_headers,data=data)
    return response.json()

def parse_one_page(rep,file,db=None):

    items = rep.get('content').get('positionResult').get('result')
    for item in items:
        city=item.get('city')
        positionname=item.get('positionName')
        workyear=item.get('workYear')
        company=item.get('companyShortName')
        salary=item.get('salary')
        companylabel=','.join(item.get('companyLabelList'))
        advantage=item.get('positionAdvantage')
        education=item.get('education')
        data={}
        data['city']=city
        data['company']=company
        data['companylable']=companylabel
        data['positionname']=positionname
        data['advantage']=advantage
        data['salary']=salary
        data['education']=education
        data['workyear']=workyear
        with open(file,'a+',encoding='utf-8') as f:
            #f.writelines(city+','+company+','+company_label+','+advantage+','+positionname+','+workyear+','+salary)
            print(city,'|',company,'|',companylabel,'|',positionname,
                  '|', advantage,'|',salary,'|',education,'|',workyear,file=f)
        if db:
            save_database(db,data)

def create_database(name):

    db=pymysql.connect(host='localhost',port=3306,user='tudou',password='123')
    cursor=db.cursor()
    cursor.execute('create database if not exists {}'.format(name))
    try:
        db.commit()
    except:
        print('database create has problem !')
        db.rollback()

    cursor.execute('use {}'.format(name))
    cursor.execute('create table if not exists %s (id int auto_increment primary key ,city varchar (255),company varchar (255),companylable text,positionname varchar(255),advantage text,salary varchar (255),education varchar (255),workyear varchar (255))' %name)
    try:
        db.commit()
    except:
        print('table create has problem !')
        db.rollback()

def save_database(name,data):

    db = pymysql.connect(host='localhost', port=3306, user='tudou', password='123',db=name,charset='utf8')
    cursor=db.cursor()

    key=','.join(data.keys())
    value=','.join(len(data)*['%s'])
    #sql="insert into {} ({}) values ({});".format(name,key,value)
    sql="insert into {} ({}) values ({});".format(name,key,value)
    cursor.execute(sql,tuple(data.values()))
    db.commit()
    db.close()


def main():
    args=parser.parse_args()
    work=args.work
    file=args.file
    db=args.db
    create_database(work)
    for i in range(15):
        print('>>>>>>>>>>>>>>start page  {}'.format(i))
        rep=get_page(work,i+1)
        parse_one_page(rep,'拉勾网'+file,db)
        time.sleep(12)

if __name__ == '__main__':
    main()