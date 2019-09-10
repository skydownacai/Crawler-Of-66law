import os
import pandas as pd
import logging as log
dir = "债权债务/"
record = 70031+97571+ 103748
print(record)
def mergeAll(files,month):
    global record
    print('starting merge month:',month)
    need = list(map(lambda x:pd.read_excel(dir + month + '/'+x),files))
    df = pd.concat(need,sort = False)
    columns = ["时间","问题","问题描述","链接地址","类型","地区"]
    for i in range(int((len(df.columns) - 6)/3)):
        columns += ["回答人{}".format(i+1),"回答","赞同数"]
    df.columns =columns
    df = df.reset_index(drop=True)
    df.to_excel(dir+month+".xls")
    num = df.shape[0]
    record += num
    print('增加:',num)
    print('done')
for month in os.listdir(dir):
    monthdatadir = dir + month
    if monthdatadir.endswith('.xls'):
        continue
    files = os.listdir(monthdatadir)
    files.sort(key = lambda x:int(x[:-4]) if 'end' not in str(x)  else 100000)
    mergeAll(files,month)
print('total:',record)