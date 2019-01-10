#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 15:49:36 2018

@author: SaiSanthosh
"""

import numpy as np
import pandas as pd
from fancyimpute import MICE
from sklearn import preprocessing
import seaborn as sns
import matplotlib.pyplot as plt


rt= pd.read_csv('rotten_predata.csv',encoding='utf-8')
rt.replace(r'\s+', np.nan, regex=True)


dummy_col=['ratings', 'month', 'release']
rt = pd.get_dummies(rt,columns=dummy_col,drop_first=True)
droplist = ['Unnamed: 0.1','audience_score','critic_score','actor_names','actor_links','synopsis',
            'In Theaters','Genre','Directed By','Runtime', 'Rating', 'Written By', 'day','genre']


rt.rename(columns={'Unnamed: 0':'id'}, inplace=True)
rt = rt.drop(droplist,axis=1)


actor1 = pd.DataFrame(rt['actor1'])
actor2 = pd.DataFrame(rt['actor2'])
actor3 = pd.DataFrame(rt['actor3'])
director1 = pd.DataFrame(rt['director1'])

rt['Box Office'] = rt['Box Office'].str.replace('$','')
rt['Box Office'] = rt['Box Office'].str.replace(',','')

###Delete aftr getting studio performance
studio = rt['Studio']
studio = pd.DataFrame(studio)
rt= rt.drop(['Studio', 'actor1', 'actor2', 'actor3', 'director1'], axis=1)



def sf(val):
    x=0
    t = {}
    for v in val:
        try:
            t[x]=float(str(v).replace(",",""))
        except:
            t[x] = 'nan'
        
        x=x+1

    g = pd.DataFrame([t])
    g=g.transpose()
    #print(g)
    return g.iloc[:,0]


rt['Box Office'] = sf(rt['Box Office'])
#rt['audience - User Ratings'] = sf(rt['audience - User Ratings'])
#rt['audience - Average Rating'] = sf(rt['audience - Average Rating'])
rt['actor1_star'] = sf(rt['actor1_star'])
rt['actor2_star'] = sf(rt['actor2_star'])
rt['actor3_star'] = sf(rt['actor3_star'])
rt['length'] = sf(rt['length'])
rt['director1_star'] = sf(rt['director1_star'])
rt['actor3_bignominations'] = sf(rt['actor3_bignominations'])


movie = rt['movie_id']
movie = pd.DataFrame(movie)


#rt = rt.replace(np.nan, '')
rating = rt['diff_rating']
rating = pd.DataFrame(rating)

rt = rt.drop(['id','diff_rating', 'movie_id'],axis=1)
rt=rt.astype(float)

X_fill = MICE().complete(rt.as_matrix())
X_fill = pd.DataFrame(X_fill)
X_fill.columns = rt.columns
X_fill = pd.concat((X_fill,rating),axis=1)

X_fill = pd.concat([X_fill, rating, studio, movie, actor1, actor2,actor3,director1], axis=1)

X_fill.to_csv('rotten_impute.csv', encoding='utf-8')
#dum = pd.concat([dum, ])
