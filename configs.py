# -*- encoding: utf-8 -*-
'''
@Description:  :
@Date          :2020/11/22 19:51:38
@Author        :a76yyyy
@version       :1.0
'''

import os
sqltype = 'mysql' 
default_dat_update = True #执行ip_Sync.py时是否默认联网自动更新czipdata.dat文件, False为默认不更新, 不存在dat文件时该选项失效。
default_txt_update = False #当数据文件版本无更新时是否默认自动更新czipdata.txt文件, False为默认不更新。
default_sql_update = True #当执行ip_Sync.py时是否默认自动更新数据库, False为默认不更新。
class mysql(object):
    host="localhost"
    port=3306
    user="root"
    password="123456"
    ip_database="czipdata"
    charset="utf8"
    connect_timeout=3
    read_timeout=5

class sqlite3(object):
    chdir=os.path.dirname(__file__)
    ip_database=os.path.join(chdir+os.path.sep+"data"+os.path.sep+"ipdata.db")

config = {
    'mysql':mysql,
    'sqlite3':sqlite3
}