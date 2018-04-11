#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 16:23:08 2018

@author: SaiSanthosh
"""

import numpy as np
import pandas as pd

rt=pd.read_csv('output1.csv',encoding='latin-1')
rt.replace(r'\s+', np.nan, regex=True)


def ratingcertificate(rating):
    r=[]
    for x in rating:
        try:
            c=x.split(' ')
            r.append(c[0])
        except:
            r.append(np.nan)
        
    ratings=pd.DataFrame([r])
    #print(ratings)
    return ratings


def runtime(duration):
    r=[]
    for d in duration:
        try:
            time=d.split(' ')
            r.append(time[0])
        except:
            r.append(np.nan)
    length = pd.DataFrame([r])
    #print(length)
    return length
            
        
def releasedate(date):
    d=[]
    m=[]
    y=[]
    for x in date:
        try:
            release=x.split('/')
            d1=release[0]
            m1=release[1]
            y1=release[2]
            d.append(d1)
            m.append(m1)
            y.append(y1)
        except:
            d.append(np.nan)
            m.append(np.nan)
            y.append(np.nan)

    day = pd.DataFrame([d])
    month = pd.DataFrame([m])
    year = pd.DataFrame([y])
    
    return day, month, year

# Processing the genre field. Splitting the genre and creating the array of genre elements for each Movie
def processGenre(genre):
    completeGenre = []
    i=0
    for eachMovieGenre in genre:
        i+=1
        movieGenre = []
        try:
            getAllGenre = eachMovieGenre.split(",")
            for getEachAllGenre in getAllGenre:
                movieGenre.append(getEachAllGenre.strip())
                completeGenre.append(movieGenre)
        except:
            completeGenre.append(None)
    return pd.DataFrame([completeGenre])
    
day, month, year = releasedate(rt.loc[:,'In Theaters'])
length=runtime(rt.loc[:,'Runtime'])
ratings=ratingcertificate(rt.loc[:,'Rating'])
# Process the genre and return the dataframe object of genre 
genre = processGenre(rt.loc[:,'Genre'])

day.index.name= 'day'
month.index.name='month'
year.index.name='year'
length.index.name='length'
ratings.index.name='ratings'

# Create the new index of the genre in the datafram
genre.index.name = 'genre'

# Concatinating all the processed data
df2=pd.concat((day, month,year,length,ratings, genre), axis=0)
df2 = df2.transpose()
df2.columns= ['day','month','year','length','ratings','genre']
final_df=pd.concat((rt,df2),axis=1)

# Generating the dummies for the genre array elements
"""
How it Works:
    .apply(Series) - converts the series of lists into dataframes
    .stack() - puts everything in one column again (Creating a multilevel index)
    pd.get_dummies - Creating the dummies
    .sum(level=0) -  for remerging the different rows that should be one row (by summing up the second level, only keeping the original level (level=0))
    
"""
t = pd.get_dummies(final_df['genre'].apply(pd.Series).stack()).sum(level=0,axis=0)

final_df = pd.concat((final_df,t), axis=1)
final_df['diff_rating']=final_df['criticRating'].sub(final_df['audienceMeter'], axis=0)
final_df['diff_rating']=abs(final_df['diff_rating'])
final_df.to_csv('pre_data.csv', encoding='utf-8')