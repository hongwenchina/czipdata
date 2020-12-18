# -*- encoding: utf-8 -*-
'''
@Description:  :将纯真IP数据库的dat文件转换为txt文本文件
@Date          :2020/10/07 23:09:46
@Author        :a76yyyy
@version       :1.0
'''
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import socket
import logging
from struct import pack, unpack
import json
import getopt
import ipUpdate
import ip_Sync
from file_set import file_set
import getopt

def usage():
    print(
        '函数功能     : 将纯真IP数据库的dat文件转换为txt文本文件.\n' +
        '外部参数输入 : \n       ' +
        '-h : 返回帮助信息,\n       '+
        '-d : 纯真IP数据库的dat文件名或路径,默认为"czipdata.dat",\n       '+
        '-t : 输出文本文件的文件名或路径,默认为"czipdata.txt",\n       '+
        '-s : 起始索引, 默认为0,\n       '+
        '-e : 结束索引, 默认为IP数据库总记录数.'
    )

# 将整数的IP转换成IP号段，例如（18433024 ---> 1.25.68.0）
def convert_int_ip_to_string(ip_int):
    return socket.inet_ntoa(pack('I', socket.htonl(ip_int)))

# IP 转换为 整数
def convert_string_ip_to_int(str_ip):
    try:
        ip = unpack('I', socket.inet_aton(str_ip))[0]
    except Exception as e:
        # 如果IP不合法返回 None
        logging.info(e)
        return None
    # ((ip >> 24) & 0xff) | ((ip & 0xff) << 24) | ((ip >> 8) & 0xff00) | ((ip & 0xff00) << 8)
    else:
        return socket.ntohl(ip)

# 转换字符
def convert_str_to_utf8(gbk_str):
    try:
        return unicode(gbk_str, 'gbk').encode('utf-8')
    except Exception as e:
        # 当字符串解码失败，并且最一个字节值为'\x96',则去掉它，再解析
        logging.info(e)
        if gbk_str[-1] == '\x96':
            try:
                return unicode(gbk_str[:-1], 'gbk').encode('utf-8') + '?'
            except Exception as e:
                logging.info(e)
                pass

        return 'None'

# 获取offset 值
def get_offset(buffer_string):
        return unpack('I', buffer_string + b'\0')[0]


class IPLoader(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.db_buffer = None
        self.open_db()
        (self.idx_start, self.idx_end, self.idx_count) = self._get_index()

    def open_db(self):
        if not self.db_buffer:
            self.db_buffer = open(self.file_name, 'rb')
        return self.db_buffer

    def _get_index(self):
        """
        读取数据库中IP索引起始和结束偏移值
        """
        self.db_buffer.seek(0)
        # 文件头 8个字节，4字节开始索引偏移值+4字节结尾索引偏移值
        index_str = self.db_buffer.read(8)
        start, end = unpack('II', index_str)
        count = (end - start) // 7 + 1
        return start, end, count

    def read_ip(self, offset):
        """
        读取ip值（4字节整数值）
        返回IP值
        """
        if offset:
            self.db_buffer.seek(offset)

        buf = self.db_buffer.read(4)
        return unpack('I', buf)[0]

    def get_offset(self, offset):
        if offset:
            self.db_buffer.seek(offset)

        buf = self.db_buffer.read(3)
        return unpack('I', buf + b'\0')[0]

    def get_string(self, offset):
        """
        读取原始字符串（以"\0"结束）
        返回元组：字符串
        """
        if offset == 0:
            return 'None'

        flag = self.get_mode(offset)

        if flag == 0:
            return 'None'

        elif flag == 2:
            offset = self.get_offset(offset + 1)
            return self.get_string(offset)

        self.db_buffer.seek(offset)

        ip_string = b''
        while True:
            ch = self.db_buffer.read(1)
            if ch == b'\0':
                break
            ip_string += ch

        return ip_string

    def get_mode(self, offset):
        # 偏移指针位置
        self.db_buffer.seek(offset)
        c = self.db_buffer.read(1)
        if not c:
            return 0
        return ord(c)

    def get_mode_offset(self):
        buf = self.db_buffer.read(3)
        return get_offset(buf)
    
    def get_ip(self,offset):
        # 移动指针位置
        self.db_buffer.seek(offset)
        buf = self.db_buffer.read(4)
        ip = socket.inet_ntoa(pack('!I', unpack('I', buf)[0]))
        return ip

    def get_ip_record(self, offset):
        # 移动指针位置
        self.db_buffer.seek(offset)

        # 获取mode
        mode = ord(self.db_buffer.read(1))

        if mode == 1:
            mode_1_offset = self.get_mode_offset()
            mode_ip_location = self.get_string(mode_1_offset)
            mode_1 = self.get_mode(mode_1_offset)
            if mode_1 == 2:
                mode_ip_info = self.get_string(mode_1_offset + 4)
            else:
                mode_ip_info = self.get_string(mode_1_offset + len(mode_ip_location) + 1)

        elif mode == 2:

            mode_ip_location = self.get_string(self.get_mode_offset())
            mode_ip_info = self.get_string(offset + 4)

        else:
            mode_ip_location = self.get_string(offset)
            mode_ip_info = self.get_string(offset + len(mode_ip_location) + 1)

        return mode_ip_location, mode_ip_info


    # 获取IP信息并写入文本文件中
    def get_ip_info(self,filename,left,right):
        ip_file = open(filename,"w")
        print('写入文件 ' + filename +' 中, 请稍候...')
        if self.idx_count - left >= right - left and right - left >= 0:
            for i in range(left,right):
                ip_offset = i
                idx_offset = self.idx_start + ip_offset * 7
                ip_start = self.get_ip(idx_offset)
                if idx_offset != self.idx_end:
                    idx2_offset = idx_offset + 7
                    nextIp = self.get_ip(idx2_offset)
                    nextIp = convert_string_ip_to_int(nextIp)
                    ip_end = convert_int_ip_to_string(nextIp-1)
                else:
                    ip_end = '255.255.255.255'
                address_offset = self.get_offset(idx_offset + 4)
                (location, info) = self.get_ip_record(address_offset + 4)
                ip_location = location.decode('gbk')
                ip_info = info.decode('gbk')
                data = [ip_start.ljust(16),ip_end.ljust(16),ip_location,' ',ip_info,'\n']
                ip_file.writelines(data)
            ip_file.writelines('\n')
            ip_file.writelines('\n')
            ip_file.writelines("IP数据库共有数据 ： " + str(right-left) + " 条\n")
            print('写入完成, 写入 ' + str(right-left) +' 条数据.')
        else:
            print('写入失败, IP数据库共' + str(self.idx_count) + '组数据, 请检查输入参数!')
        ip_file.close()


if __name__ == '__main__':
    """
    @description  :将纯真IP数据库的dat文件转换为txt文本文件
    ---------
    @params  :-d : 纯真IP数据库的dat文件名或路径,默认为"czipdata.dat"
             -t : 输出文本文件的文件名或路径,默认为"czipdata.txt"
             -s : 起始索引, 默认为0
             -e : 结束索引, 默认为IP数据库总记录数
    -------
    @Returns  :None
    -------
    """
    opts,args = getopt.getopt(sys.argv[1:],'-h-d:-t:-s:-e:',['help','datfile=','txtfile=','start=','end='])
    varlist = []
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        if opt_name in ('-d','--datfile'):
            dat_filename = opt_value
            q = IPLoader(dat_filename)
            varlist.append('dat_filename')
        if opt_name in ('-t','--txtfile'):
            txt_filename = opt_value
            varlist.append('txt_filename')
        if opt_name in ('-s','--start'):
            startIndex = int(opt_value)
            varlist.append('startIndex')
        if opt_name in ('-e','--end'):
            endIndex = int(opt_value)
            varlist.append('endIndex')

    tmp_dir = os.path.abspath(os.path.dirname(__file__)+os.path.sep+"tmp")
    file_set(tmp_dir,'dir')
    data_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))+os.path.sep+"data")
    file_set(data_dir,'dir')
    if 'dat_filename' not in varlist:
        dat_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
        if not file_set(dat_filename):
            ip_Sync.down(dat_filename)
        q = IPLoader(dat_filename)
    if 'txt_filename' not in varlist:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        file_set(txt_filename)
    if 'startIndex' not in varlist:
        startIndex = 0
    if 'endIndex' not in varlist:
        endIndex = q.idx_count
    q.get_ip_info(txt_filename,startIndex,endIndex)