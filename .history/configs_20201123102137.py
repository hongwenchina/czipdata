# -*- encoding: utf-8 -*-
'''
@Description:  :
@Date          :2020/11/22 19:51:38
@Author        :a76yyyy
@version       :1.0
'''

import os
sqltype = 'mysql' 

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