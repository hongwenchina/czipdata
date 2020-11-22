# -*- encoding: utf-8 -*-
'''
@Description:  :实现纯真IP数据库的下载和更新.
@Date          :2020/11/03 13:27:05
@Author        :a76yyyy
@version       :1.0
'''

import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import ipUpdate
import dat2txt
from database import mysql_Database
from configs import config
from dat2mysql import dat2mysql
from collegeUpdate import collegeUpdate
from convert import convert
from file_set import file_set

tmp_dir = os.path.abspath(os.path.dirname(__file__)+os.path.sep+"tmp")
file_set(tmp_dir,'dir')
data_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))+os.path.sep+"data")
file_set(data_dir,'dir')

def down(filename= None):
    """
    @description  :从纯真网络(cz88.net)导入qqwry.dat至指定dat格式文件名.
    ---------
    @param  :filename : 输出纯真IP数据库的dat文件名或路径,默认为"../data/czipdata.dat".
    -------
    @Returns  :None
    -------
    """
    varlist = []
    if filename == None:
        filename =  os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
        file_set(filename)
    version_file = os.path.abspath(data_dir+os.path.sep+"czipdata_version.bin")
    file_set(version_file)
    ret = ipUpdate.datdown(filename,version_file)
    if ret > 0:
        print('成功写入到%s, %s字节' %
              (filename, format(ret, ','))
            )
        print( "------------------------------------------- \n " )
    elif ret == 0:
        print( "------------------------------------------- \n " )
    else:
        print('写入失败, 错误代码: %d' % ret)
        print( "------------------------------------------- \n " )

def dat2Txt(dat_filename= None, txt_filename= None, startIndex= None, endIndex= None):
    """
    @description  :将纯真IP数据库的dat文件转换为txt文本文件
    ---------
    @params  :dat_filename : 纯真IP数据库的dat文件名或路径,默认为"../data/czipdata.dat"
             txt_filename : 输出文本文件的文件名或路径,默认为"../data/czipdata.txt"
             startIndex : 起始索引, 默认为0
             endIndex : 结束索引, 默认为IP数据库总记录数
    -------
    @Returns  :None
    -------
    """

    if dat_filename == None:
        dat_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
        if not file_set(dat_filename):
            down(dat_filename)
    q = dat2txt.IPLoader(dat_filename)
    if txt_filename == None:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        file_set(txt_filename)
    if startIndex == None:
        startIndex = 0
    if endIndex == None:
        endIndex = q.idx_count
    ip_info = q.get_ip_info(txt_filename,startIndex,endIndex)

def dat2Mysql(mysql_object,ip_tablename= None, txt_filename= None):
    """
    @description  :将纯真IP数据库的txt文件转换至mysql数据库指定表中
    ---------
    @params  :ip_tablename : mySQL中IP数据库的表名,默认为"iprange_info"
             txt_filename : 输入文本文件的文件名或路径,默认为"../data/czipdata.txt"
    -------
    @Returns  :None
    -------
    """
    
    if txt_filename == None:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        if not file_set(txt_filename):
            dat2Txt(txt_filename= txt_filename)
    if ip_tablename == None:
        ip_tablename = 'iprange_info'
    mysql = mysql_object
    dat2mysql(mysql,ip_tablename,txt_filename)

def collegeupdate(collegeJson= None, college_tablename= None):
    """
    @description  :从'https://github.com/pg7go/The-Location-Data-of-Schools-in-China'导入'大学-8084.json'至指定json格式文件名.
    ---------
    @param  :collegeJson : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".
             college_tablename : mySQL中IP数据库的大学信息表的表名,默认为"college_info"
    -------
    @Returns  :None
    -------
    """
    
    if collegeJson == None:
        collegeJson =  os.path.abspath(tmp_dir+os.path.sep+"college.json")
    if college_tablename == None:
        college_tablename = 'college_info'
    collegeUpdate(filename, college_tablename)

def convertipv4(mysql_object,college_tablename= None,num_config= None,start_id= None,college_filename= None,correct_filename= None):
    """
    @description :将纯真IP数据库内的地址细分为省市区
    ---------
    @params :num_config : 每次处理ip信息的记录数, 默认为20000.
             start_id : 处理ip信息的起始记录索引值, 默认为1.
             college_tablename : mySQL中IP数据库的大学信息表的表名,默认为"college_info".
             college_filename : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".
             correct_filename : 自定义纠错文件的json文件名或路径,默认为"../data/correct.json".
    -------
    @Returns  :None
    -------
    """
    if num_config == None:
        num_config = 20000 
    if start_id == None:
        start_id = 1
    if college_tablename == None:
        college_tablename = 'college_info'
    if college_filename == None:
        college_filename =  os.path.abspath(tmp_dir+os.path.sep+"college.json")
    if correct_filename == None:
        correct_filename =  os.path.abspath(data_dir+os.path.sep+"correct.json")
        file_set(correct_filename)
    
    convert(mysql_object,college_tablename,num_config,start_id,college_filename,correct_filename)

def sqldump(mysql_object):
    print( "连接IP数据库, 并导出为sql文件: \n---------------处理中, 请稍候---------------")
    sql_file = os.path.abspath(data_dir+os.path.sep+"ipdatabase.sql")
    os.system('mysqldump -h %s -P %s -u %s -p%s %s > %s' % (config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, sql_file))
    print( "IP数据库导出成功! ")
    table_college_info_sql_file = os.path.abspath(data_dir+os.path.sep+"college_info.sql")
    table_iprange_info_sql_file = os.path.abspath(data_dir+os.path.sep+"iprange_info.sql")
    os.system('mysqldump -h %s -P %s -u %s -p%s %s college_info > %s' % (config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_college_info_sql_file))
    print( "高校信息表导出成功! ")
    os.system('mysqldump -h %s -P %s -u %s -p%s %s iprange_info > %s' % (config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_iprange_info_sql_file))
    print( "IP数据表导出成功! ")
    
if __name__ == '__main__':
    """
    @description  :实现纯真IP数据库的下载和更新.
    ---------
    @params  :None
    -------
    @Returns  :None
    -------
    """
    filename =  os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
    if os.path.exists(filename):
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        if os.path.exists(txt_filename):
            #dat2Txt(txt_filename= txt_filename)
            pass
    mysql = mysql_Database(config['mysql'].ip_database)
    dat2Mysql(mysql)
    convertipv4(mysql)
    sqldump(mysql)