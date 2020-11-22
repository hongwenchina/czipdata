# -*- encoding: utf-8 -*-
'''
@Description:  :
@Date          :2020/10/08 20:22:15
@Author        :a76yyyy
@version       :1.0
'''
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from database import mysql_Database
from configs import config
import socket
import struct
import ipUpdate
from file_set import file_set
import getopt

def usage():
    print(
        '函数功能     : 将纯真IP数据库的txt文件转换至mysql数据库指定表中.\n' +
        '外部参数输入 : \n       ' +
        '-h : 返回帮助信息,\n       '+
        '-t : mySQL中IP数据库的表名,默认为"iprange_info",\n       '+
        '-f : 输入文本文件的文件名或路径,默认为"../data/czipdata.txt"'
    )

def save_data_to_mysql(mysql_object, ip_line):
    try:

        begin = ip_line[0:16].replace(' ', '')
        end = ip_line[16:32].replace(' ', '')
        item = ip_line[32:].split(" ")
        try:
            location = item[0]

        except:
            location = ''
        try:
            isp_type= ' '.join(str(i) for i in item[1:]).split('\n')[0]
        except Exception as e:
            print(e)
            isp_type = ''

        this_line_value = (begin, struct.unpack("!I",socket.inet_aton(begin))[0], end, struct.unpack("!I",socket.inet_aton(end))[0], location, isp_type)
        return this_line_value
    except Exception as e:
        print(e)

def dat2mysql(mysql_object,ip_tablename,txt_filename):
    print('检索ip数据库是否存在 \n---------------处理中, 请稍候---------------')
    mysql = mysql_object
    code='DROP TABLE IF EXISTS `'+ ip_tablename +'`;'
    mysql.execute(code)
    code='''
    CREATE TABLE IF NOT EXISTS `'''+ ip_tablename +'''` (
        `id` int AUTO_INCREMENT NOT NULL COMMENT '主键',
        `ip_start` varchar(32) NOT NULL COMMENT '起始IP',
        `ip_start_num` bigint(20) NOT NULL COMMENT 'IP起始整数',
        `ip_end` varchar(32) NOT NULL COMMENT '结束IP',
        `ip_end_num` bigint(20) NOT NULL COMMENT 'IP结束整数',
        `country` varchar(200) NOT NULL DEFAULT '' COMMENT '国家/地区/组织',
        `province` varchar(200) NOT NULL DEFAULT '' COMMENT '省/自治区/直辖市',
        `city` varchar(200) NOT NULL DEFAULT '' COMMENT '地级市',
        `area` varchar(200) NOT NULL DEFAULT '' COMMENT '县/区/镇/街道',
        `address` varchar(200) NOT NULL DEFAULT '' COMMENT '详细地址',
        `location` varchar(200) NOT NULL DEFAULT '' COMMENT '运营商/节点',
        `UpdateTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP() COMMENT '更新日期',
        PRIMARY KEY (`id`),
        KEY `idx_start_end_number` (`ip_start_num`,`ip_end_num`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;
    '''
    mysql.execute(code)
    ip_file = open(txt_filename)
    print('将IP数据文件"'+ txt_filename +'"导入Mysql数据库中: \n---------------处理中, 请稍候---------------')
    ary = []
    i = 0
    j = 0
    insert_sql = 'INSERT  INTO `'+ ip_tablename +'` (`ip_start`, `ip_start_num`, `ip_end`, `ip_end_num`, `address`, `location`, `UpdateTime`) VALUES ( %s, %s, %s, %s, %s, %s, DEFAULT )'
    for line in ip_file:
        z=line
        ary.append(save_data_to_mysql(mysql, z))
        i = i+1
        if '255.255.255.0' in z:
            break
        if len(ary)>=100000:
            mysql.insert(insert_sql, ary)
            print("本批次（行：" + str(j) + " - " + str(j+99999) + "）已处理完成。共需处理" + str(100000) + "条，成功转换" + str(i-j) + "条。")
            j = j +100000
            print("系统将自动处理下一批IP数据（行：" + str(j) + " - " + str(j+99999) + "）…… \n---------------处理中, 请稍候---------------")
            ary = []
    if ary and len(ary)>0:
        mysql.insert(insert_sql, ary)
        print( "本批次（行：" + str(j) + " - " + str( j + len(ary) -1) + "）已处理完成。共需处理" + str(len(ary)) + "条，成功转换" + str(i-j) + "条。" )
        print( "-------------------------------------------" )
        print('已全部导入完成, 共导入'+str(i)+'条数据.\n')
        ary = []
    ip_file.close()

if __name__ == '__main__':
    """
    @description  :将纯真IP数据库的txt文件转换至mysql数据库指定表中
    ---------
    @params  :-t : mySQL中IP数据库的ip信息表的表名,默认为"iprange_info"
             -f : 输入文本文件的文件名或路径,默认为"../data/czipdata.txt"
    -------
    @Returns  :None
    -------
    """
    opts,args = getopt.getopt(sys.argv[1:],'-h-t:-f:',['help','tablename=','txtfile='])
    varlist = []
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        if opt_name in ('-t','--tablename'):
            ip_tablename = opt_value
            varlist.append('ip_tablename')
        if opt_name in ('-t','--txtfile'):
            txt_filename = opt_value
            varlist.append('txt_filename')
    tmp_dir = os.path.abspath(os.path.dirname(__file__)+os.path.sep+"tmp")
    file_set(tmp_dir,'dir')
    data_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))+os.path.sep+"data")
    file_set(data_dir,'dir')
    if 'ip_tablename' not in varlist:
        ip_tablename = 'iprange_info'
    if 'txt_filename' not in varlist:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        if not file_set(txt_filename):
            ipUpdate.dat2txt(txt_filename= txt_filename)
    mysql_object = mysql_Database(config['mysql'].ip_database)
    dat2mysql(mysql_object,ip_tablename,txt_filename)