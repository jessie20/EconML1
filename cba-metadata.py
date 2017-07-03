# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 13:14:30 2016

@author: elliott
"""

import pandas as pd
import os
from collections import defaultdict
from datetime import date

os.chdir('/home/elliott/research/corpora/union_contracts/michigan/')

#df = pd.read_excel('michigan_cba_metadata.xlsx')
#
#contract_lists = defaultdict(list)
#
#output = []
#
#for i, row in df.iterrows():    
#    datadict = {}
#    for x in ['filename','district', 'C','F','O','P','T','X',
#              'filedate_year','filedate_month','filedate_day','E']:    
#        datadict[x] = row[x]
#        
#    if not pd.isnull(row.Union1) and '-' in row.Union1:
#        unions1 = row.Union1.split('-')
#    else:
#        unions1 = [row.Union1]
#    if not pd.isnull(row.Union2) and '-' in str(row.Union2):
#        unions2 = row.Union2.split('-')
#    else:
#        unions2 = [row.Union2]
#    unions = '_'.join(sorted([x for x in unions1 + unions2 if not pd.isnull(x)]))
#    datadict['unions'] = unions
#    output.append(datadict)
#    
#newdf = pd.DataFrame(output)
#newcols = ['filename', 'district', 'filedate_year', 'filedate_month',
#       'filedate_day', 'unions', 'E', 'C', 'F', 'O', 'P', 'T', 'X']
#       
#newdf[newcols].to_excel('metadata-cbas.xlsx', index=False)

df = pd.read_excel('metadata-cbas.xlsx')

contract_lists = defaultdict(list)

for i, row in df[df.E==1].iterrows():
    
    only_teachers = True                    
    for x in ['C','F','O','P','T','X']:
        if row[x] == 1:
            only_teachers = False
            break
    
    exp_year = row.filedate_year
    last_year = row.filedate_year - 1
    
    try:
        month = int(row.filedate_month)
    except:
        month = 6
    try:
        day = int(row.filedate_day)
    except:
        day = 30
    exp_date = date(exp_year,month,day)
    
    contract_lists[row['district']].append([last_year, exp_date, row['unions'], only_teachers,row.file_id])

out_data = []
    
for district in contract_lists:
    
    contracts = contract_lists[district]    
    contracts.sort(key=lambda x: x[0])        
    
    start_year = 2004
    
    for year in range(2004, 2016):

        if year > contracts[-1][0]:
            data = {'district':district, 
                    'year': year, 
                    'contract_start': contracts[-1][0]+1, 
                    'contract_end': 2015,
                    'unions': contracts[-1][2],
                    'only_teachers': contracts[-1][3],
                    'file_id': contracts[-1][4]}
                        
            out_data.append(data)  
            continue        
            
        for i, c in enumerate(contracts):
            if year >= start_year and year <= c[0]:
                
                end_year = c[0]
                
                if i > 0:
                    start_year = contracts[i-1][0]+1 # get year after previous last year
                
                data = {'district':district, 
                        'year': year, 
                        'contract_start': start_year, 
                        'contract_end': end_year,
                        'unions': c[2],
                        'only_teachers': c[3],
                        'file_id': c[4]}
                        
                out_data.append(data)
                break


df2 = pd.DataFrame(out_data)[['district','year','contract_start','contract_end',
                             'unions','only_teachers', 'file_id']]
                             
df2['pp'] = (df2['year'] >= 2010).astype(int)
df2['pp_contract'] = (df2['contract_start'] >= 2010).astype(int)
df2['rtw'] = (df2['year'] >= 2013).astype(int)
df2['rtw_contract'] = (df2['contract_start'] >= 2013).astype(int)
    
df2.to_csv('contract-year-data.csv')    

#####

cba_df = pd.read_csv('/home/elliott/research/corpora/union_contracts/michigan/contract-year-data.csv')

test_df = pd.read_csv('/home/elliott/research/projects/ashmacnaidu/teachers/data/merged.csv')
    
test_df['year'] = test_df['schoolyear'] + 2000

del(test_df['schoolyear'])

df3 = pd.merge(cba_df, test_df, on=('district','year'),how='outer')
    
df3.to_csv('tests-contracts-merged.csv')    
