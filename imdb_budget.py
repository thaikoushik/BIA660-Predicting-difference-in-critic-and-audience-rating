#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 03:12:46 2018

@author: SaiSanthosh
"""

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import os


#writing datafile to rt
rt=pd.read_csv('/Users/SaiSanthosh/Desktop/BIA660/Project/output3.csv',encoding='latin-1')
rt.replace(r'\s+', np.nan, regex=True)



start = 0

#Creating a file to write scraped data
if os.path.exists('test_budget.txt'): 
    with open('test_budget.txt','r') as fo: 
        start = len(fo.readlines())
    f=open('test_budget.txt','a+')
else:
    f=open('test_budget.txt','a+')


#Web Driver
ua=UserAgent()
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)
service_args=['--ssl-protocol=any','--ignore-ssl-errors=true']
driver = webdriver.Chrome(desired_capabilities=dcap,service_args=service_args)



def imdb_budget(movie_name):
   
    #To login into imdbpro
    driver.get('http://www.imdb.com/')
    
    #searches for login button
    imdbPro = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="navProMenu"]/p/a/img')))
    imdbPro.click()
    
    #clicks on imdblogin
    loginButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="header_message"]/a')))
    loginButton.click()
    
    login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_with_imdb_expender"]')))
    login.click()
    
    ###entering login details
    driver.find_element_by_xpath('//*[@id="ap_email"]').send_keys('munna.saisanthosh@gmail.com')
    driver.find_element_by_xpath('//*[@id="ap_password"]').send_keys('Stevens_123')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="signInSubmit"]'))).click()
    
    x=start
     
    #creating dictionaries
    budget = {}
    weekend = {}
    gross_us={}
    gross_ww={}
     
   
    #passing movie into loop 
    for n in movie_name[start:20].iterrows():
        print(x+1)
        
        gross_us[x] = 'nan'
        gross_ww[x] = 'nan'
        budget[x] = 'nan'
        weekend[x] = 'nan'
        ####passing movie name
        search = driver.find_element_by_xpath('//*[@id="searchField"]')
        search.clear()
        search.send_keys(n[1]['Title'])
        
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_container"]/form/a'))).click()
        #time.sleep(10)
        
        ### Refines search- selecting only movies
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="TITLE"]'))).click()
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="type"]/ul/li[1]/label'))).click()
        
        try:
            ###clicks on first result
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results"]/ul/li[1]/ul/li[1]/span/a'))).click()
            
            try:
                ###selects main details header where we have all info
                head = driver.find_element_by_xpath('//*[@id="main_details"]').text
                #print(head)
                new = head.split('\n')
                
                ###Sparsing data into required dictionary
                for i in range(len(new)):
                    try:
                        if new[i] == 'BUDGET':
                            b=new[i+1].split('(')
                            budget[x] = b[0]
                        
                    except:
                        budget[x] = 'nan'
                    try:
                        if new[i] == 'OPENING WKD':
                            w = new[i+1].split('(')
                            weekend[x] = w[0]
                        
                    except:
                        weekend[x] = 'nan'
                    try:
                        if new[i] == 'GROSS':
                            if '|' in new[i+1]:
                                g=new[i+1].split('|')
                                g1 = g[0].split('(')
                                g3=g1[0]
                                g2= g[1].split('(')
                                g4 = g2[0]
                            else:
                                g = new[i+1].split('(')
                                g3= g[0]
                                g4 = 'nan'

                            gross_us[x] = g3
                            gross_ww[x] = g4
                        
                    except:
                        gross_us[x] = 'nan'
                        gross_ww[x] = 'nan'
                    
                    
                    
            except NoSuchElementException:
                print('Exception')
        
        except (NoSuchElementException,TimeoutException):
            print('Exception')
                
        
        f.write(str(x+1)+'\t')
        f.write(str(n[1]['Title'])+'\t')
        f.write(str(budget.get(x))+'\t'+str(weekend.get(x))+'\t'+str(gross_us.get(x))+'\t'+str(gross_ww.get(x))+'\n')
        x=x+1
        
    #converting dictionaries to dataframes
    budget = pd.DataFrame([budget])
    weekend = pd.DataFrame([weekend])
    gross_us = pd.DataFrame([gross_us])
    gross_ww = pd.DataFrame([gross_ww])
    
    return budget,weekend,gross_us, gross_ww, x


def movienames_split(title):
    t=[]
    for name in title:
        if len(name) < 5:
            t.append(name)
        else:
            try:
                n1 = name.split('(')
                t.append(n1[0])
            except:
                t.append(np.nan)
            
    movie_name = pd.DataFrame([t])
    movie_name = movie_name.transpose()
    movie_name.columns = ['Title']
    
    return movie_name
 

     

movie_name = movienames_split(rt.loc[:,'Movie Name'])
budget, weekend, gross_us, gross_ww, final = imdb_budget(movie_name)


#result = directors("Zack Snyder")

f.close()

#concatinating all the dictionaries
df1=pd.concat(( budget, weekend, gross_us, gross_ww), axis=0)
df1 = df1.transpose()
df= pd.DataFrame(columns=['Movie Title','budget', 'weekend', 'gross_us', 'gross_ww'])
df=pd.concat((movie_name['Title'][start:final],df1),axis=1)  

#writing all the scrapped data into excel file

if os.path.exists('imdb_budget.csv'): 
    with open('imdb_budget.csv', 'a+') as imdb:
        df.to_csv(imdb, header=False, na_rep = np.nan, encoding='utf-8')
else:
    with open('imdb_budget.csv', 'a+') as imdb:
        df.to_csv(imdb, header=True, na_rep = np.nan, encoding='utf-8')
