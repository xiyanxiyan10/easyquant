import pandas as pd
import argparse
from datetime import datetime
from dateutil import parser
import sys

import pdb


def timestamp2day(timestamp):
    datetime_obj = parser.parse(timestamp)
    formatted_date = datetime_obj.strftime('%Y-%m-%d')
    return formatted_date

def set_columns(df):
    new_columns = df.iloc[0].tolist()  # 假设第一行作为列标识
    df.columns = new_columns
    df = df[1:]  # 删除第一行作为列标识的行
    return df

def reverse_line(df):
    return  df[::-1]

def check_null(df):
    null_rows = df[df.isnull().any(axis=1)]
    num_null_rows = len(null_rows)
    return num_null_rows


def parse_args():
    parse = argparse.ArgumentParser(description='input origin csv file, output clean csv file')  # 2、创建参数对象
    parse.add_argument('-i', '--input', default='input.csv', type=str, help='input csv file path')  # 3、往参数对象添加参数
    parse.add_argument('-o', '--output', default='output.csv', type=str, help='output csv file path')
    args = parse.parse_args()  # 4、解析参数对象获得解析对象
    return args

args = parse_args()

df = pd.read_csv(args.input, encoding= 'utf-8',header=None)
#pdb.set_trace()

df =  set_columns(df)
df['Date'] = df['Date'].apply(timestamp2day)
df = reverse_line(df)
print(df)

missing_count = check_null(df)
if missing_count > 0:
    print("missing count:%d" % missing_count)
else:
    print("generate output csv")
    df.to_csv(args.output, index=False, header=False)
