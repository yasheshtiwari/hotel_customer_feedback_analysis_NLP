# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 09:00:11 2018

@author: Kumary
"""

import pandas as pd
import numpy as np
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

df = pd.read_csv("customer_reviews.csv");
df_tx = pd.read_csv("taxonomy.csv");

def asterix_handler(asterixw, lookupw):
    mtch = "F"
    for word in asterixw:
        for lword in lookupw:
            if(word[-1:]=="*"):
                if(bool(re.search("^"+ word[:-1],lword))==True):
                    mtch = "T"
                    break
                return(mtch)

def remov_punct(withpunct):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    without_punct = ""
    char = 'nan'
    for char in withpunct:
        if char not in punctuations:
            without_punct = without_punct + char
            return(without_punct)

def remov_quote(withquote):
    quote = '"'
    without_quote = ""
    char = 'nan'
    for char in withquote:
        if char not in quote:
            without_quote = without_quote + char
            return(without_quote)

#Split each document by sentences and append one below the other for sentence level topic mapping.
sentence_data = pd.DataFrame(columns=['slno','text'])
for d in range(len(df)):    
    doc = (df.iloc[d,1].split('.'))
    for s in ((doc)):        
        temp = {'slno': [df['slno'][d]], 'text': [s]}
        sentence_data=  pd.concat([sentence_data,pd.DataFrame(temp)])
        temp = ""


#Drop empty text rows if any and export data
        
sentence_data['text'].replace('',np.nan,inplace=True);      
sentence_data.dropna(subset=['text'], inplace=True);  

data = sentence_data
cat2list = list(set(df_tx['Subtopic']))
#data = pd.concat([data,pd.DataFrame(columns = list(cat2list))])            
data['Category'] = 0
mapped_data = pd.DataFrame(columns = ['slno','text','Category']);
temp=pd.DataFrame()
for k in range(len(data)):
    comment = remov_punct(data.iloc[k,1])
    data_words = [str(x.strip()).lower() for x in str(comment).split()]
    data_words = filter(None, data_words)
    output = []

    for l in range(len(df_tx)):
        key_flag = False
        and_flag = False
        not_flag = False
        if (str(df_tx['PrimaryKeywords'][l])!='nan'):
            kw_clean = (remov_quote(df_tx['PrimaryKeywords'][l]))
        if (str(df_tx['AdditionalKeywords'][l])!='nan'):
            aw_clean = (remov_quote(df_tx['AdditionalKeywords'][l]))
        else:
            aw_clean = df_tx['AdditionalKeywords'][l]
        if (str(df_tx['ExcludeKeywords'][l])!='nan'):
            nw_clean = remov_quote(df_tx['ExcludeKeywords'][l])
        else:
            nw_clean = df_tx['ExcludeKeywords'][l]
            Key_words = 'nan'
            and_words = 'nan'
            and_words2 = 'nan'
            not_words = 'nan'
            not_words2 = 'nan'

        if(str(kw_clean)!='nan'):
            key_words = [str(x.strip()).lower() for x in kw_clean.split(',')]
            key_words2 = set(w.lower() for w in key_words)

        if(str(aw_clean)!='nan'):
            and_words = [str(x.strip()).lower() for x in aw_clean.split(',')]
            and_words2 = set(w.lower() for w in and_words)

        if(str(nw_clean)!= 'nan'):
            not_words = [str(x.strip()).lower() for x in nw_clean.split(',')]
            not_words2 = set(w.lower() for w in not_words)

        if(str(kw_clean) == 'nan'):
            key_flag = False        
        else:
            if set(data_words) & key_words2:
                key_flag = True
            else:
                if(asterix_handler(key_words2, data_words)=='T'):
                    key_flag = True

        if(str(aw_clean)=='nan'):
            and_flag = True
        else:
            if set(data_words) & and_words2:
                and_flag = True
            else:
                if(asterix_handler(and_words2,data_words)=='T'):
                    and_flag = True
        if(str(nw_clean) == 'nan'):
            not_flag = False
        else:
            if set(data_words) & not_words2:
                not_flag = True
            else:
                if(asterix_handler(not_words2, data_words)=='T'):
                    not_flag = True
                    if(key_flag == True and and_flag == True and not_flag == False):
                        output.append(str(df_tx['Subtopic'][l]))            
            temp = {'slno': [data.iloc[k,0]], 'text': [data.iloc[k,1]], 'Category': [df_tx['Subtopic'][l]]}
mapped_data = pd.concat([mapped_data,pd.DataFrame(temp)])
    #data['Category'][k] = ','.join(output)

#output mapped data
mapped_data.to_csv("mapped_data.csv",index = False)