# -*- encoding: utf-8 -*-
'''
@Description:  :
@Date          :2020/11/22 22:19:13
@Author        :a76yyyy
@version       :1.0
'''

import os,sys
from dat2mysql import save_data_to_mysql
def sqlExport():

    code='''
    CREATE TABLE IF NOT EXISTS `'''+ ip_tablename +'''` (
        `id` int AUTO_INCREMENT NOT NULL COMMENT '主键',
        `ip_start` varchar(32) NOT NULL COMMENT '起始IP',
        `ip_start_num` bigint(20) NOT NULL COMMENT 'IP起始整数',
        `ip_end` varchar(32) NOT NULL COMMENT '结束IP',
        `ip_end_num` bigint(20) NOT NULL COMMENT 'IP结束整数',
        `country` varchar(200) COMMENT '国家/地区/组织',
        `province` varchar(200) COMMENT '省/自治区/直辖市',
        `city` varchar(200) COMMENT '地级市',
        `area` varchar(200) COMMENT '县/区/镇/街道',
        `address` varchar(200) COMMENT '详细地址',
        `location` varchar(200) COMMENT '运营商/节点',
        `UpdateTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP() COMMENT '更新日期',
        PRIMARY KEY (`id`),
        KEY `idx_start_end_number` (`ip_start_num`,`ip_end_num`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;
    '''
    ip_file = open(txt_filename)
    sql_file = open(sql_filename,'w')
    sql_file.write(code)
    print('将IP数据文件"'+ txt_filename +'"导入sql脚本中: \n---------------处理中, 请稍候---------------')
    i = 0
    j = 0
    for line in ip_file:
        z=line
        ary = save_data_to_mysql(None, z)
        i = i+1
        insert_sql = 'INSERT  INTO `'+ ip_tablename +'` (`ip_start`, `ip_start_num`, `ip_end`, `ip_end_num`, `address`, `location`, `UpdateTime`) VALUES ("'+ary[0]+'","'+ary[1]+'","'+ary[2]+'","'+ary[3]+'","'+ary[4]+'","'+ary[5]+'", DEFAULT )'
        sql_file.write(insert_sql)
        if '255.255.255.0' in z:
            break
    print('已全部导入完成, 共导入'+str(i)+'条数据.\n')
    ip_file.close()
    
