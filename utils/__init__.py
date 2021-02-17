from ._logging import *
from .compress import *
from .pipetools import *
from .ajax_operator import *
from .excel_operator import *

import os
import re
import shutil
import string
from dateutil import parser
from datetime import datetime, date


# 解析时间
def parse_datetime(datetime_data):
    try:
        if repr(type(datetime_data)) == "<class 'pywintypes.datetime'>":
            return datetime.strptime(str(datetime_data.date()), '%Y-%m-%d')
        elif isinstance(datetime_data, date):
            return datetime.strptime(str(datetime_data), '%Y-%m-%d')
        else:
            return parser.parse(datetime_data)
    except:
        return datetime_data


# 解析数字
def parse_num(num_data):
    try:
        if isinstance(num_data, str):
            if re.search(r'\d+\.?\d*', num_data):
                if int(float(num_data)) == float(num_data):
                    num_data = str(int(float(num_data)))
                else:
                    num_data = float(num_data)
        elif isinstance(num_data, float):
            if num_data == int(num_data):
                num_data = str(int(num_data))
        elif isinstance(num_data, int):
            num_data = str(num_data)
    finally:
        return num_data


# 提取数字
def extract_num(num_data):
    try:
        num_regex = re.compile(r'\d+\.?\d*')
        if isinstance(num_data, str):
            regex_result = num_regex.search(num_data)
            if regex_result:
                num_data = regex_result.group()
    finally:
        return num_data


# 将字符串的标点符号替换为空格
def clean_punctuation(dirty_str):
    punctuation = string.punctuation + '！”“￥、·（），。：；《》？【】……\\n'
    return re.sub(rf'[{punctuation}]', ' ', dirty_str)


# 移动文件
def move_file(source_path, destination_path):
    # shutil.move(source_path, destination_path)
    # todo: 测试阶段使用复制的方式
    shutil.copy(source_path, destination_path)
    return destination_path


# 在指定文件夹寻找带指定关键字的最新修改的文件(非文件夹)
def find_latest_modified_file_with_keyword(dir_path, keyword: (str, list) = ''):
    if isinstance(keyword, str):
        keyword = [keyword]
    files = os.listdir(dir_path)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=True)
    for file in files:
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path) and all([each in file for each in keyword]):
            return move_file(file_path, os.path.join(config.TMP_DIR, file))
    else:
        rpa_logger.info(f"找不到带KEYWORD {','.join(keyword)} 的文件")


if __name__ == '__main__':
    print(parse_num('200SETS'))
