# -*- encoding: utf-8 -*-
'''
@Description:  :
@Date          :2020/10/08 20:22:08
@Author        :a76yyyy
@version       :1.0
'''
import pymysql
import sqlite3
import os
from configs import mysql
from func_timeout import func_set_timeout,exceptions

class mysql_Database(object):
    host = mysql.host
    port = mysql.port
    user = mysql.user
    password = mysql.password
    charset = mysql.charset

    def __init__(self,*args):
        if len(args) == 1:
            self.db = args[0]
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, charset=self.charset)
        elif len(args) == 2:
            self.db = args[0]
            self.connect_timeout = args[1]
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, charset=self.charset, connect_timeout=self.connect_timeout)
        elif len(args) == 3:
            self.db = args[0]
            self.connect_timeout = args[1]
            self.read_timeout = args[2]
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, charset=self.charset, connect_timeout=self.connect_timeout, read_timeout=self.read_timeout)
        else:
            print('参数输入错误')
            exit()
        self.cursor = self.connection.cursor()

    def insert(self, query, params):
        try:
            self.cursor.executemany(query, params)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def execute(self,code):
        try:
            self.cursor.execute(code)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def executemany(self,code,slist):
        try:
            self.cursor.executemany(code,slist)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def query(self, query, *args):
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)# 得到一个可以执行SQL语句并且将结果作为字典返回的游标
        result = None
        timeout = None
        if args:
            if len(args) == 1:
                timeout = args[0]
        if timeout:
            @func_set_timeout(timeout)
            def timelimited():
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                return result
            try:
                result = timelimited()
            except exceptions.FunctionTimedOut:
                print("timeout!")
                self.cursor.close()
                return result
        else:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
        return result

    def __del__(self):
        self.connection.close()

class sqlite3_Database(object):
    
    def __init__(self,db_file):
        if os.path.isfile(db_file):
            os.remove(db_file)
        #self.connection
        self.cursor = self.connection.cursor()

    def insert(self, query, params):
        try:
            self.cursor.executemany(query, params)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def execute(self,code):
        try:
            self.cursor.execute(code)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def query(self, query):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query)
        return cursor.fetchall()

    def __del__(self):
        self.connection.close()