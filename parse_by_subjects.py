# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 10:19:34 2016

@author: elliott
"""

from glob import glob
from spacy.en import English
from collections import Counter, defaultdict
from random import shuffle
import pandas as pd
import re
from process_contract import process_contract
import os

def recurse(*tokens):
    children = []
    def add(tok):       
        sub = tok.children
        for item in sub:
            children.append(item)
            add(item)
    for token in tokens:
        add(token)    
    return children
    
def get_branch(t,sent,include_self=True):        
    branch = recurse(t)
    if include_self:
        branch += [t]
        
    #branch = [m for m in branch if m.dep_ != 'punct' and not m.orth_.isdigit()]
    branch = [w for w in sent if w in branch]# and w.dep_ in include]

    lemmas = []
    tags = []
    
    for token in branch:
        lemma = token.lemma_.lower()
        #if len(lemma) <= 2:
        #    continue
        if any([char.isdigit() for char in lemma]):
            continue
        if any(punc in lemma for punc in ['.',',',':',';', '-']):
            continue
        lemmas.append(lemma)
        tags.append(token.tag_)
    
    #tags = [w.tag_ for w in sent if w in mods]
    return lemmas, tags
    


subjectnorm = {'teacher':'teacher',
               'employee':'teacher',
               'worker':'teacher',
               'staff':'teacher',
               
               'board':'district',
               'district':'district',
               'superintendent':'district',
               'employer':'district',
               
               'union':'union',
               'association': 'union',
               'member': 'union',
               'representative':'union', 
               'cea':'union',
               'president':'union',
               'mea':'union',
               
               'principal':'principal',
               'administration':'principal',
               'administrator':'principal',
               'supervisor':'principal',
               'director':'principal'}
             
other = ['agreement',
             'day',
             'assignment','leave','payment',
             'he/she','they','party']

subdeps = ['nsubj','nsubjpass', 'expl']

conditionals = ['if','when','unless']
                #'where', 'whereas','whenever', 'provided that', 'in case']

maindeps = ['nsubj','nsubjpass', 
              'expl', # existential there as subject
              'advmod', 
              'dobj',
              'prep',
              'xcomp',
              'dative', # indirect object
              'advcl',
              'agent',
              'ccomp',
              
              'acomp',
              'attr']

           
           
def parse_by_subject(sent, docnum, secnum, sentnum):
    
    subjects = [t for t in sent if t.dep_ in subdeps]

    datalist = []

    for obnum, subject in enumerate(subjects):   
        subdep = subject.dep_                             
        
        mlem = None
        verb = subject.head
        if not verb.tag_.startswith('V'):
            continue        
            
        vlem = verb.lemma_
        
        tokenlists = defaultdict(list)
        
        #if 'if' in tokcheck:
        #    print(sent)
        #    raise
                
        neg = ''
        for t in verb.children:
            if t.tag_ == 'MD':
                mlem = t.orth_.lower()
                continue
            dep = t.dep_
            if dep in ['punct','cc','det', 'meta', 'intj', 'dep']:
                continue
            if dep == 'neg':
                neg = 'not'                
            elif t.dep_ == 'auxpass':
                vlem = t.orth_.lower() + '_' + vlem
            elif t.dep_ == 'prt':
                vlem = vlem + '_' + t.orth_.lower()                    
            #elif dep in maindeps:
            #    tokenlists[dep].append(t)
            else:
                #pass
                #print([modal,vlem,t,t.dep_,sent])
                #dcount[t.dep_] += 1
                tokenlists[dep].append(t)
            
        slem = subject.lemma_                    

        data = {'docid':  docnum, 
                'secnum': secnum,
                'sentnum': sentnum,
                'obnum': obnum,
                'subject': slem,
                'modal':mlem,
                'neg': neg,
                'verb': vlem,
                #'full_sentence': str(sent),
                #'subfilter': 0,
                'passive': 0,
                'md': 0}
        
        if slem in subjectnorm:
            data['subjectnorm'] = subjectnorm[slem]
        if subdep == 'nsubjpass':
            data['passive'] = 1
        if mlem is not None:
            data['md'] = 1
        
        subphrase, subtags = get_branch(subject,sent,include_self=False)                                        
        
        data['subject_branch'] = subphrase        
        data['subject_tags'] = subtags
        
        object_branches = []
        object_tags = []
        
        for dep, tokens in tokenlists.items():
            if dep in subdeps:
                continue
            for t in tokens:
                tbranch, ttags = get_branch(t,sent)                
                object_branches.append(tbranch)
                object_tags.append(ttags)

            
    
        #if len(object_branches) > 0:
            #for x in object_phrases:
            #    if any(b in x for b in conditionals):
            #        print(x,sent,data)
            #data['object_phrases'] = ';'.join(object_phrases)
        data['object_branches'] = object_branches
        data['object_tags'] = object_tags        
        
        #data['topic_lemmas'] otherlemmas
        #data['topic_tags'] = othertags
        
        #if data['md']:
        #    print(data['object_branches'])

            
        datalist.append(data)
    
    return datalist   

def process_header(header):
    h = header.lower()
    words = h.split()
    return ' '.join(words[2:])

nlp = English()

os.chdir('/home/elliott/Dropbox/Ash_Jayathilak_Sabat/data/')

filenames = glob('txt/*/*.txt')
#shuffle(filenames)
filenames.sort()
oblist = []        
headerlist = []

doc2file = {}

headerlengths = []

not_contracts = ['txt/teachers/05040_2010-08-31_MEA_E_P_X.txt',
                 'txt/teachers/05065_2010-08-31_MEA_E.txt'
                 'txt/teachers/05065_2013_EEA_E.txt'
                 ]

print('note:replacing and/or with or')
for i,fname in enumerate(filenames):        
    print(fname)
    doc2file[i] = fname
    
    if fname in not_contracts:
        continue
    # this will tag and parse the whole document
    rawtext = open(fname,'rt').read()
    
    sections, headers = process_contract(rawtext)
    
    headerlengths.append(len(sections))
    if len(sections) < 5:
        print(fname,len(sections),len(rawtext))

    for header in headers:
        headerlist.append(process_header(header))        
    
    for j, section in enumerate(sections):
        
        section = re.sub('and/or','or',section)
  
        doc = nlp(section)

        for k, sent in enumerate(doc.sents):   
            
            tokcheck = str(sent).split()
                
            if any([x.isupper() and len(x) > 3 for x in tokcheck]):
                continue
            
            #for x in conditionals:
            #    if x in tokcheck:
            #        print(sent)
                                  
            oblist += parse_by_subject(sent, i, j, k)                      
            
#pd.to_pickle(oblist,'/home/research/projects/ashmacnaidu/teachers/analysis/parsed-1.pkl')
pd.to_pickle(doc2file,'analysis/doc2file.pkl')
df = pd.DataFrame(oblist)
df.to_pickle('analysis/parsed-df-1.pkl')

    