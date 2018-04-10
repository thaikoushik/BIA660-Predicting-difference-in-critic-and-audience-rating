#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 01:09:02 2018

@author: SaiSanthosh
"""

import pandas as pd
import numpy as np
from sklearn import metrics
from fancyimpute import KNN, MICE as m
import matplotlib.pyplot as plt
import seaborn as sns


df= pd.read_csv('pre_data.csv')

df.rename(columns={'Unnamed: 0':'id'}, inplace=True)
#df.drop('', axis=1, inplace=True)
#df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1)

df=df.drop(['Movie Name', 'In Theaters','Genre', 'Runtime','Studio','criticConsensus','actors','Written By','synopsis',
         'criticReviews','topAudienceReviews','criticRating','audienceMeter','Rating',
         'Directed By','On Disc/Streaming','day'],axis=1)


dummy_col=['tomatoMeter', 'ratings', 'month']
final_data = pd.get_dummies(df,columns=dummy_col,drop_first=True)
#final_data['audience - User Ratings']=final_data['audience - User Ratings'].convert_objects(convert_numeric=True)
final_data['audience - Average Rating']=final_data['audience - Average Rating'].convert_objects(convert_numeric=True)

for d in final_data['audience - Average Rating']:
    if d== 'N':
        d.append(np.nan)
    else:
        continue
    
#final_data.to_csv('checking.csv', encoding='utf-8')    


nans = lambda df: df[df.isnull().any(axis=1)]
X_incomplete=nans(final_data)

X_new = X_incomplete.drop(['id'],axis=1)
#fancyimpute.MICE().complete(final_data)
df2=pd.DataFrame(data=KNN(k=3).complete(X_new), columns=X_new.columns, 
                 index=X_new.index)

df_id=pd.DataFrame(X_incomplete['id'])
df3 = pd.concat((df_id,df2),axis=1)
 
final = final_data.update(df3)

final_data.set_index('id', inplace=True)
df3.set_index('id', inplace=True)
final_data.update(df3)
              
#final_data.to_csv('checking.csv', encoding='utf-8')

final_data.reset_index(drop = True, inplace = True)

X = final_data.drop('diff_rating',axis=1)
y = final_data['diff_rating']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=101)

from sklearn.linear_model import LinearRegression, r2_score

lm = LinearRegression()
lm.fit(X_train,y_train)
print('Coefficients: \n', lm.coef_)
print("R2: ", lm.score)
predictions = lm.predict( X_test)
#plt.scatter(y_test,predictions)
#plt.xlabel('Y Test')
#plt.ylabel('Predicted Y')


print('MAE:', metrics.mean_absolute_error(y_test, predictions))
print('MSE:', metrics.mean_squared_error(y_test, predictions))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, predictions)))

coeffecients = pd.DataFrame(lm.coef_,X.columns)
coeffecients.columns = ['Coeffecient']
coeffecients

r2_score(y_test, predictions)


plt.scatter(X_test, y_test,  color='black')
plt.plot(X_test, predictions, color='blue', linewidth=3)