# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 13:14:30 2016

@author: elliott
"""

import pandas as pd
import os
from collections import defaultdict
from datetime import date

os.chdir('/home/elliott/research/projects/ashmacnaidu/teachers/analysis/metadata/')

df = pd.read_excel('michigan-metadata-2016-05-02.xlsx')
meta2text = pd.read_pickle('meta2text.pkl')

contract_lists = defaultdict(list)

for i, row in df[df.E==1].iterrows():
    
    if row.not_contract == 1:
        continue
    
    only_teachers = True                    
    for x in ['C','F','O','P','T','X']:
        if row[x] == 1:
            only_teachers = False
            break
    
    if not pd.isnull(row.expdate_year):        
        expyear = row.expdate_year
    else:
        expyear = row.filedate_year
    
    try:
        effyear = int(row.effdate_year)
    except:
        effyear = None
    
    data = {'file_id': row.file_id,
            'effyear':effyear,
            'expyear':int(expyear), 
            'unions': row['unions'], 
             'only_teachers':only_teachers}
    contract_lists[row['district']].append(data)

out_data = []
    
# note: some contract overlap in the same district-year
    
for district in contract_lists:
    
    contracts = contract_lists[district]    
    contracts.sort(key=lambda x: x['expyear'])
    
    endyear = 2004
    
    for i,contract in enumerate(contracts):
        startyear = contract['effyear']
        if pd.isnull(startyear):
            startyear = endyear
        endyear = contract['expyear']        
        for year in range(startyear,endyear):
            data = {'district':district, 
                    'year': year, 
                    'contract_start': startyear,
                    'contract_end': endyear,
                    'unions': contract['unions'],
                    'only_teachers': contract['only_teachers'],
                    'metaid': contract['file_id'],
                    'textid': meta2text[contract['file_id']]}
            out_data.append(data)  
 
df2 = pd.DataFrame(out_data)[['district','year','contract_start','contract_end',
                             'unions','only_teachers', 'metaid','textid']]

df2.only_teachers = df2.only_teachers.astype(int)                             
df2['pp'] = (df2['year'] >= 2010).astype(int)
df2['pp_contract'] = (df2['contract_start'] >= 2010).astype(int)
df2['rtw'] = (df2['year'] >= 2013).astype(int)
df2['rtw_contract'] = (df2['contract_start'] >= 2013).astype(int)
    
df2.to_csv('contract-year-data.csv',index=False)    