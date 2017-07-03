# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:56:33 2016

@author: elliott
"""

import os
import pandas as pd


def set_provision_types(df):
    
    STRICT_MODALS = ['shall','must','will']
    PERMISSIVE_MODALS = ['may','can']
    OBLIGATION_VERBS = ['require', 'expect', 'compel', 'oblige', 'obligate']
    CONSTRAINT_VERBS = ['prohibit', 'forbid', 'ban', 'bar', 'restrict', 'proscribe']
    
    df['negword'] = df['neg']
    
    df['neg'] = df.neg == 'not'
        
    # strict modals are shall, must, and will
    df['strict_modal'] = df['modal'].isin(STRICT_MODALS)
    
    # permissive modals are may and can
    df['permissive_modal'] = df['modal'].isin(PERMISSIVE_MODALS)
    
    df['modality'] = 0
    
    df['modality'] = df['modality'] + 1 * (df['permissive_modal']) + 2 * (df['strict_modal'])
    
    # obligation verbs 
    df['obligation_verb'] = df['passive'] & df['verb'].isin(OBLIGATION_VERBS)
                                                                               
    # constraint verbs 
    df['constraint_verb'] = df['passive'] & df['verb'].isin(CONSTRAINT_VERBS)

    # permissiion verbs are be allowed, be permitted, and be authorized
    df['permission_verb'] = df['passive'] & df['verb'].isin(['allow', 'permit', 'authorize'])
    
    df['entitlement_verb'] = df['verb'].isin(['have', 'receive','retain'])
    
    df['special_verb'] = df['obligation_verb'] | df['constraint_verb'] | df['permission_verb'] | df['entitlement_verb']         
    
    df['active_verb'] = ~df['passive'] & ~df['special_verb']
    
    df['verb_type'] = 0 + 1 *df['passive'] + 2*df['obligation_verb'] + 3*df['constraint_verb'] + 4*df['permission_verb'] + 5*df['entitlement_verb']
   
    df['obligation'] = (
                        (~df['neg'] & df['strict_modal'] & df['active_verb']) | # positive, strict modal, action verb
                        (~df['neg'] & df['strict_modal'] & df['obligation_verb']) | #positive, strict modal or non-modal, obligation verb
                         (~df['neg'] & ~df['md'] & df['obligation_verb'])
                        ) 
    
    df['constraint'] = (
                        (df['neg'] & df['md'] & ~df['obligation_verb']) | # negative, any modal, any verb except obligation verb
                        (~df['neg'] & df['strict_modal'] & df['constraint_verb']) # positive, strict modal, constraint verb
                        )
                        
                        
    df['permission'] = (
                        (~df['neg'] & ( (df['permissive_modal'] & df['active_verb']) | 
                        df['permission_verb'])) | 
                        (df['neg'] & df['constraint_verb'])
                        )
                        
                        
    df['entitlement'] = ( 
                        (df['entitlement_verb']) |
                        (~df['neg'] & df['strict_modal'] & df['passive']) |
                        (df['neg'] & df['obligation_verb'])
                        )
    
    for x in ['neg','strict_modal','permissive_modal','permission_verb',
              'entitlement_verb','passive_verb', 'constraint_verb', 'active_verb','obligation_verb',
              'constraint','obligation','permission','entitlement']:
                  df[x] = df[x].astype(int)
       
    replacer = {'will':'shall',
                'must':'shall',
                'can':'may',
                None:''}
    df.replace({"modal": replacer},inplace=True)
        
    df['verbstr'] = df['modal'] + ' ' + df['negword'] + ' ' + df['verb']
    df['verbstr'] = df['verbstr'].str.replace('  ',' ').str.strip().str.replace(' ','_')    

    return df
    
    

def verb_counts(df):
    allcounts = {}
    verbcounts = {'teacher':{},
                  'union':{},
                  'district':{},
                  'principal':{},}
                  
    for neg in [False,True]:
        for modality in [0,1,2]:
            for verb_type in [0,1,2,3,4,5]:
                allcounts[neg,modality,verb_type]=df[(df.neg==neg)&(df.modality==modality)&(df.verb_type==verb_type)]['verbstr'].value_counts()[:10]
                for agent in verbcounts.keys():              
                    verbcounts[agent][neg,modality,verb_type]=df[(df.subjectnorm==agent)&(df.neg==neg)&(df.modality==modality)&(df.verb_type==verb_type)]['verbstr'].value_counts()[:100]
    
    
    return verbcounts
    
    for agent in verbcounts:
        for verbtype in verbcounts[agent]:
            print(agent+','+str(','.join(str(int(x)) for x in verbtype))+','+' '.join(list(verbcounts[agent][verbtype].index)))
        
    for verbtype in allcounts:
        print(str(';'.join(str(int(x)) for x in verbtype))+';'+', '.join(list(allcounts[verbtype].index)))
        

os.chdir('/home/research/projects/ashmacnaidu/teachers/analysis/')        
df = pd.read_pickle('parsed-df-1.pkl')
df = set_provision_types(df)

df['textid'] = df['docid']

df = df[['textid', 'md', 'modal', 'neg', 
       'obnum', 'secnum', 'sentnum', 
       'subjectnorm', 'verb', 'negword', 
       'strict_modal',
       'permissive_modal', 'modality', 'obligation_verb', 'constraint_verb',
       'permission_verb', 'entitlement_verb', 'special_verb', 'passive_verb',
       'active_verb', 'verb_type', 'obligation', 'constraint', 'permission',
       'entitlement', 'verbstr']]

df.to_pickle('df-statements-verbs.pkl')
