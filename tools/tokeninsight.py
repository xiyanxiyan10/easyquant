import pandas as pd
from datetime import datetime
from dateutil import parser

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

df = pd.read_csv('./input.csv',encoding= 'utf-8',header=None)
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
    df.to_csv('output.csv', index=False, header=False)
