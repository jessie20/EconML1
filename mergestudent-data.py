# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 19:03:00 2016

@author: elliott
"""

import pandas as pd
from glob import glob
import os
from collections import defaultdict

os.chdir('/home/elliott/research/projects/ashmacnaidu/teachers/data/')

files = glob('*csv')
files.sort()

year_vars = ['SchoolYear','DESCRIPTION', 'SCHOOL_YEAR']
district_vars = ['DistrictCode', 'District Code','ResidentDistrictNumber']
building_vars = ['BuildingCode', 'Building Code']

skip_vars = ['year', 'ISDCode', 'ISDName','district', 'DistrictName', 
             'LOCALE_NAME','SORT_ORDER', 'BuildingName']

level_vars = ['LOCATION_TYPE', 'EntityType']

group_vars = ['EFFECTIVENESS_CATEGORY', 'ASSIGNMENT_TYPE']

outcome_vars = []

datadict = {}    

districtdict = {}

years = set()

yearvardict = defaultdict(set)

keepcols = ['school','district','year'] + []

column_set = set()

for f in files:    
    if 'bc5ff8ab-9f55-4407-8199-f793024a6167' in f:
        continue
    #print(f)
    df = pd.read_csv(f)
    
    if 'MathScoreAverage' not in df.columns:        
        continue
    
    for yvar in year_vars:
        df.rename(columns={yvar: 'year'}, inplace=True)
    df['year'] = pd.to_numeric(df['year'].str.slice(0,2))     
    year = list(df.year)[0]
    
    if 'Subgroup' in df.columns:
        #print(df.Subgroup.value_counts())
        df = df[df['Subgroup'] == 'All Students']
        
    if 'Building Code' in df.columns:
        df.rename(columns={'Building Code': 'BuildingCode'}, inplace=True)   
    if 'BuildingCode' not in df.columns:
        continue             
    df['BuildingCode'] = pd.to_numeric(df['BuildingCode'],errors='coerce')
    df = df[df.BuildingCode > 0]
    df['BuildingCode'] = df['BuildingCode'].astype(int)
    df['school'] = df['BuildingCode']
    
    for dvar in district_vars:
        df.rename(columns={dvar: 'district'}, inplace=True)
        
    #df = df[keepcols]
        
#    for c in df.columns:
#        try:
#            if max(df[c]) > 0:
#                yearvardict[c].add(year)
#        except:
#            pass
    
    if len(df[df.duplicated('school')]) == 0:        
        for i, row in df.iterrows():
            s = row.school
            t = year
            
            if s not in districtdict:
                districtdict[s] = row.district
                
            if (s,t) not in datadict:
                datadict[s,t] = {}
            for c in df.columns:
                if c in year_vars + district_vars + building_vars + level_vars + group_vars + skip_vars:
                    continue   
                if c in datadict[s,t]:
                    print(c)
                    raise
                    continue
                datadict[s,t][c] = row[c]
    
    else:
        print(list(df.columns))
        print()
    
output = []

for (s,t) in datadict:
    
    out = {}
    
    out['school'] = s
    out['schoolyear'] = t
    
    d = districtdict[s]
    
    out['district'] = d
    
    for k in datadict[s,t]:
        out[k] = datadict[s,t][k]
    output.append(out)
    
df2 = pd.DataFrame(output)

outcols = [
     'district',
     'school',
     'schoolyear',
     'AFRICAN_AMERICAN_ENROLLMENT',
     'DROPOUT_RATE_4_YEAR',
     'DROPOUT_RATE_5_YEAR',
     'DROPOUT_RATE_6_YEAR',
     'GRADE_11_ALL_SUBJECT_PERCENT_READY',
     'GRADE_11_ENGLISH_PERCENT_READY',
     'GRADE_11_ENROLLMENT',
     'GRADE_11_MATH_AVG_SS',
     'GRADE_11_MATH_PERCENT_READY',
     'GRADE_11_MATH_PROFICIENT',
     'GRADE_11_MATH_TESTED',
     'GRADE_11_READING_AVG_SS',
     'GRADE_11_READING_PERCENT_READY',
     'GRADE_11_READING_PROFICIENT',
     'GRADE_11_READING_TESTED',
     'GRADE_11_SCIENCE_AVG_SS',
     'GRADE_11_SCIENCE_PERCENT_READY',
     'GRADE_11_SCIENCE_PROFICIENT',
     'GRADE_11_SCIENCE_TESTED',
     'GRADE_11_SOCIAL_STUDIES_AVG_SS',
     'GRADE_11_SOCIAL_STUDIES_PROFICIENT',
     'GRADE_11_SOCIAL_STUDIES_TESTED',
     'GRADE_11_WRITING_AVG_SS',
     'GRADE_11_WRITING_PROFICIENT',
     'GRADE_11_WRITING_TESTED',
     'GRADE_12_ENROLLMENT',
     'GRADE_1_ENROLLMENT',
     'GRADE_2_ENROLLMENT',
     'GRADE_3_ENROLLMENT',
     'GRADE_3_MATH_AVG_SS',
     'GRADE_3_MATH_PROFICIENT',
     'GRADE_3_MATH_TESTED',
     'GRADE_3_READING_AVG_SS',
     'GRADE_3_READING_PROFICIENT',
     'GRADE_3_READING_TESTED',
     'GRADE_4_ENROLLMENT',
     'GRADE_4_MATH_AVG_SS',
     'GRADE_4_MATH_PROFICIENT',
     'GRADE_4_MATH_TESTED',
     'GRADE_4_READING_AVG_SS',
     'GRADE_4_READING_PROFICIENT',
     'GRADE_4_READING_TESTED',
     'GRADE_5_ENROLLMENT',
     'GRADE_5_MATH_AVG_SS',
     'GRADE_5_MATH_PROFICIENT',
     'GRADE_5_MATH_TESTED',
     'GRADE_5_READING_AVG_SS',
     'GRADE_5_READING_PROFICIENT',
     'GRADE_5_READING_TESTED',
     'GRADE_5_SCIENCE_AVG_SS',
     'GRADE_5_SCIENCE_PROFICIENT',
     'GRADE_5_SCIENCE_TESTED',
     'GRADE_6_ENROLLMENT',
     'GRADE_6_MATH_AVG_SS',
     'GRADE_6_MATH_PROFICIENT',
     'GRADE_6_MATH_TESTED',
     'GRADE_6_READING_AVG_SS',
     'GRADE_6_READING_PROFICIENT',
     'GRADE_6_READING_TESTED',
     'GRADE_6_SOCIAL_STUDIES_AVG_SS',
     'GRADE_6_SOCIAL_STUDIES_PROFICIENT',
     'GRADE_6_SOCIAL_STUDIES_TESTED',
     'GRADE_7_ENROLLMENT',
     'GRADE_7_MATH_AVG_SS',
     'GRADE_7_MATH_PROFICIENT',
     'GRADE_7_MATH_TESTED',
     'GRADE_7_READING_AVG_SS',
     'GRADE_7_READING_PROFICIENT',
     'GRADE_7_READING_TESTED',
     'GRADE_8_ENROLLMENT',
     'GRADE_8_MATH_AVG_SS',
     'GRADE_8_MATH_PROFICIENT',
     'GRADE_8_MATH_TESTED',
     'GRADE_8_READING_AVG_SS',
     'GRADE_8_READING_PROFICIENT',
     'GRADE_8_READING_TESTED',
     'GRADE_8_SCIENCE_AVG_SS',
     'GRADE_8_SCIENCE_PROFICIENT',
     'GRADE_8_SCIENCE_TESTED',
     'GRADE_9_ENROLLMENT',
     'GRADE_9_SOCIAL_STUDIES_AVG_SS',
     'GRADE_9_SOCIAL_STUDIES_PROFICIENT',
     'GRADE_9_SOCIAL_STUDIES_TESTED',
     'GRADUATION_RATE_4_YEAR',
     'GRADUATION_RATE_5_YEAR',
     'GRADUATION_RATE_6_YEAR']
 
df2[outcols].to_csv('merged.csv',index=False)


    
    