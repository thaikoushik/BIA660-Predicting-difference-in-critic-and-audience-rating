#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 01:03:28 2018

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
import os, re


###Reading output csv data into dataframe
rt=pd.read_csv('/Users/SaiSanthosh/Desktop/BIA660/Project/output3.csv',encoding='latin-1')
rt.replace(r'\s+', np.nan, regex=True)
rt.loc[:,'actors'] = rt.loc[:,'actors'].astype(str)
rt.loc[:,'Written By'] = rt.loc[:,'Written By'].astype(str)
rt.loc[:,'Directed By'] = rt.loc[:,'Directed By'].astype(str)


#Web Driver
ua=UserAgent()
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)
service_args=['--ssl-protocol=any','--ignore-ssl-errors=true']
driver = webdriver.Chrome(desired_capabilities=dcap,service_args=service_args)


###Function to get directors list
def directorslist(directors):
    first = directors.loc[:,'director1'].to_dict()
    second = directors.iloc[:,'director2'].to_dict()
    
    
    final = {}
    
    x = 0
    for i in first.values():
        final[x] = i
        x = x+1
        
    for i in second.values():
        final[x] = i
        x=x+1

    
    direct = set(final.values())
    direct_list= list(direct)
    
    with open('test_directorlist.txt','a+') as f:
        for i in direct_list:
            f.write(str(i)+'\n')
    
    return direct_list


#function to get directors rank and awards
def directorstarmeter(direct_list):
    
    start = 0
    
    if os.path.exists('test_director.txt'): 
        with open('test_director.txt','r') as fo: 
            start = len(fo.readlines())
            f=open('test_director.txt','a+')
    else:
        f=open('test_director.txt','a+')
    
    driver.get('http://www.imdb.com/')
    
    #searches for login button
    imdbPro = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="navProMenu"]/p/a/img')))
    imdbPro.click()
    
    #clicks on imdblogin
    loginButton = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="header_message"]/a')))
    loginButton.click()
    
    login = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_with_imdb_expender"]')))
    login.click()
    
    ###entering login details
    driver.find_element_by_xpath('//*[@id="ap_email"]').send_keys('munna.saisanthosh@gmail.com')
    driver.find_element_by_xpath('//*[@id="ap_password"]').send_keys('Stevens_123')
    WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="signInSubmit"]'))).click()
    
    #creating dictionaries
    name_d = {}
    star_d = {}
    oscars_d = {}
    another_Wins_d = {}
    nominations_d = {}
    bignominations_d = {}
    
    y=start
   
    #passing movie into loop 
    for n in direct_list[start+1:]:

        name_d[y] = n
        print(y+1)
        
        ####passing writer name
        search = driver.find_element_by_xpath('//*[@id="searchField"]')
        search.clear()
        search.send_keys(n)
        
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_container"]/form/a'))).click()
        #time.sleep()
        
        ### Refines search- selecting only directors
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="NAME"]'))).click()
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="profession"]/ul/li[3]/label'))).click()
        
        oscars_d[y] = 'nan'
        another_Wins_d[y]='nan'
        nominations_d[y] = 'nan'
        bignominations_d[y] = 'nan'
            
        try:
            ###clicks on first result
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results"]/ul/li[1]/ul/li[1]/span/a'))).click()
            rank = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="meter"]/span[1]/span[2]'))).text
            star_d[y] = rank
            
            try:
                ###selects main details header where we have all info abt awards
                head = driver.find_element_by_xpath('//*[@id="main_details"]/div/div[1]/dl[1]/dd[2]').text
                #print(head)
                new = head.split()
                ###Sparsing data into required dictionary
                for i in range(len(new)):
                    try:
                        if new[i] == 'Oscars.':
                            if not new[i-2] == 'for':
                                oscars_d[y]=new[i-1]
                        elif new[i] == 'Oscar.':
                            if not new[i-2] == 'for':
                                oscars_d[y] = new[i-1]
                        elif new[i] == 'wins':
                            another_Wins_d[y] = new[i-1]
                        elif new[i] == 'win':
                            another_Wins_d[y] = new[i-1]
                        elif new[i] == 'nominations':
                            nominations_d[y] = new[i-1]
                        elif new[i] == 'nomination':
                            nominations_d[y] = new[i-1]
                        elif new[i] == 'for':
                            bignominations_d[y] = new[i+1]
                            
                    except:
                        print('Exception')
                        
            except : 
                print('Exception')
            
        except : 
            print('Exception')
            
        
        f.write(str(y+1)+'\t')
        f.write(str(n)+'\t')
        f.write(str(star_d.get(y))+str(oscars_d.get(y))+'\t'+str(another_Wins_d.get(y))+'\t'+str(nominations_d.get(y))+'\t'+str(bignominations_d.get(y))+'\n')
        y=y+1
        
    f.close()        
    name_d = pd.DataFrame([name_d])
    name_d = name_d.transpose()       
    rank_d = pd.DataFrame([star_d])
    rank_d = rank_d.transpose()
    oscars_d = pd.DataFrame([oscars_d])
    oscars_d = oscars_d.transpose()
    another_Wins_d = pd.DataFrame([another_Wins_d])
    another_Wins_d = another_Wins_d.transpose()
    nominations_d = pd.DataFrame([nominations_d])
    nominations_d = nominations_d.transpose()
    bignominations_d = pd.DataFrame([bignominations_d])
    bignominations_d = bignominations_d.transpose()
    
    return name_d ,rank_d, oscars_d, nominations_d, another_Wins_d, bignominations_d

###function to get writers list into set
def writerslist(writers):
    first = writers.loc[:,'writer1'].to_dict()
    second = writers.loc[:,'writer2'].to_dict()
    
    
    final = {}
    
    x = 0
    for i in first.values():
        final[x] = i
        x = x+1
        
    for i in second.values():
        final[x] = i
        x=x+1

    
    write = set(final.values())
    write_list= list(write)
    
    with open('test_writerlist.txt','a+') as f:
        for i in write_list:
            f.write(str(i) + '\n')
    
    return write_list


#function to get writers ranks and awards
def writerstarmeter(write_list):
    
    start = 0
    
    if os.path.exists('test_writer.txt'): 
        with open('test_writer.txt','r') as fo: 
            start = len(fo.readlines())
            f=open('test_writer.txt','a+')
    else:
        f=open('test_writer.txt','a+')
    
    driver.get('http://www.imdb.com/')
    
    #searches for login button
    imdbPro = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="navProMenu"]/p/a/img')))
    imdbPro.click()
    
    #clicks on imdblogin
    loginButton = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="header_message"]/a')))
    loginButton.click()
    
    login = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_with_imdb_expender"]')))
    login.click()
    
    ###entering login details
    driver.find_element_by_xpath('//*[@id="ap_email"]').send_keys('munna.saisanthosh@gmail.com')
    driver.find_element_by_xpath('//*[@id="ap_password"]').send_keys('Stevens_123')
    WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="signInSubmit"]'))).click()
    
    #creating dictionaries
    name_w = {}
    star_w = {}
    oscars_w = {}
    another_Wins_w = {}
    nominations_w = {}
    bignominations_w = {}
    
    y=start
   
    #passing movie into loop 
    for n in write_list[start+1:]:
        
        
        name_w[y] = n
        print(y+1)
        
        ####passing writer name
        search = driver.find_element_by_xpath('//*[@id="searchField"]')
        search.clear()
        search.send_keys(n)
        
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_container"]/form/a'))).click()
        #time.sleep()
        
        ### Refines search- selecting only actors
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="NAME"]'))).click()
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="profession"]/ul/li[4]/label'))).click()
        
        oscars_w[y] = 'nan'
        another_Wins_w[y]='nan'
        nominations_w[y] = 'nan'
        bignominations_w[y] = 'nan'
                        
        try:
            ###clicks on first result
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results"]/ul/li[1]/ul/li[1]/span/a'))).click()
            rank = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="meter"]/span[1]/span[2]'))).text
            star_w[y] = rank
            
            try:
                ###selects main details header where we have all info abt awards
                head = driver.find_element_by_xpath('//*[@id="main_details"]/div/div[1]/dl[1]/dd[2]').text
                new = head.split()
                ###Sparsing data into required dictionary
                for i in range(len(new)):
                    try:
                        if new[i] == 'Oscars.':
                            if not new[i-2] == 'for':
                                oscars_w[y]=new[i-1]
                        elif new[i] == 'Oscar.':
                            if not new[i-2] == 'for':
                                oscars_w[y] = new[i-1]
                        elif new[i] == 'wins':
                            
                            another_Wins_w[y] = new[i-1]
                        elif new[i] == 'win':
                            another_Wins_w[y] = new[i-1]
                        elif new[i] == 'nominations':
                            nominations_w[y] = new[i-1]
                        elif new[i] == 'nomination':
                            nominations_w[y] = new[i-1]
                        elif new[i] == 'for':
                            bignominations_w[y] = new[i+1]
                            
                    except:
                       print('Exception')

                        
            except : 
                print('Exception')
                
        except : 
            print('Exception')
        
        f.write(str(y+1)+'\t')
        f.write(str(n)+'\t')
        f.write(str(star_w.get(y))+str(oscars_w.get(y))+'\t'+str(another_Wins_w.get(y))+'\t'+str(nominations_w.get(y))+'\t'+str(bignominations_w.get(y))+'\n')
        y=y+1
     
    f.close()    
    name_w = pd.DataFrame([name_w]) 
    name_w = name_w.transpose()       
    rank_w = pd.DataFrame([star_w])
    rank_w = rank_w.transpose()
    oscars_w = pd.DataFrame([oscars_w])
    oscars_w = oscars_w.transpose()
    another_Wins_w = pd.DataFrame([another_Wins_w])
    another_Wins_w = another_Wins_w.transpose()
    nominations_w = pd.DataFrame([nominations_w])
    nominations_w = nominations_w.transpose()
    bignominations_w = pd.DataFrame([bignominations_w])
    bignominations_w = bignominations_w.transpose()
    
    return name_w ,rank_w, oscars_w, nominations_w, another_Wins_w, bignominations_w

##function to get actors list
def actorslist(actors):
    first = actors.loc[:,'actor1'].to_dict()
    second = actors.loc[:,'actor2'].to_dict()
    third = actors.loc[:,'actor3'].to_dict()
    fourth = actors.loc[:,'actor4'].to_dict()
    fifth = actors.loc[:,'actor5'].to_dict()
    
    final = {}
    
    x = 0
    for i in first.values():
        final[x] = i
        x = x+1
        
    for i in second.values():
        final[x] = i
        x=x+1
        
    for i in third.values():
        final[x] = i
        x=x+1
        
    for i in fourth.values():
        final[x] = i
        x=x+1
        
    for i in fifth.values():
        final[x] = i
        x=x+1
    
    action = set(final.values())
    act_list= list(action)
    
    with open('test_actorlist.txt','a+') as f:
        for i in act_list:
            f.write(str(i)+'\n')
            
    return act_list
    

###function to get actors rank and awards
def actorstarmeter(act_list):
    
    start = 0
    
    if os.path.exists('test_actor.txt'): 
        with open('test_actor.txt','r') as fo: 
            start = len(fo.readlines())
            f=open('test_actor.txt','a+')
    else:
        f=open('test_actor.txt','a+')
    
    driver.get('http://www.imdb.com/')
    
    #searches for login button
    imdbPro = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="navProMenu"]/p/a/img')))
    imdbPro.click()
    
    #clicks on imdblogin
    loginButton = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="header_message"]/a')))
    loginButton.click()
    
    login = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_with_imdb_expender"]')))
    login.click()
    
    ###entering login details
    driver.find_element_by_xpath('//*[@id="ap_email"]').send_keys('munna.saisanthosh@gmail.com')
    driver.find_element_by_xpath('//*[@id="ap_password"]').send_keys('Stevens_123')
    WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="signInSubmit"]'))).click()
    
    #creating dictionaries
    name = {}
    star = {}
    oscars = {}
    another_Wins = {}
    nominations = {}
    bignominations = {}
    
    y=start
   
    #passing movie into loop 
    for n in act_list[start+1:]:
        
        name[y] = n
        print(y+1)
        ####passing movie name
        search = driver.find_element_by_xpath('//*[@id="searchField"]')
        search.clear()
        search.send_keys(n)
        
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_container"]/form/a'))).click()
        #time.sleep(10)
        
        ### Refines search- selecting only actors
        WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="NAME"]'))).click()
        #WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="type"]/ul/li[1]/label'))).click()
        
        oscars[y] = 'nan'
        another_Wins[y] = 'nan'
        nominations[y] = 'nan'
        bignominations[y] = 'nan'
                
        try:
            ###clicks on first result
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results"]/ul/li[1]/ul/li[1]/span/a'))).click()
            rank = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//*[@id="meter"]/span[1]/span[2]'))).text
            star[y] = rank
           
            try:
                ###selects main details header where we have all info abt awards
                head = driver.find_element_by_xpath('//*[@id="main_details"]/div/div[1]/dl[1]/dd[2]').text
                new = head.split()
               
                ###Sparsing data into required dictionary
                for i in range(len(new)):
                    try:
                     
                        if new[i] == 'Oscars.':
                            if not new[i-2] == 'for':
                                oscars[y]=new[i-1]
                           
                        if new[i] == 'Oscar.':
                            if not new[i-2] == 'for':
                                oscars[y] = new[i-1]
                        
                        if new[i] == 'wins':
                            another_Wins[y] = new[i-1]
                        if new[i] == 'win':
                            another_Wins[y] = new[i-1]
                          
                        if new[i] == 'nominations':
                            nominations[y] = new[i-1]
                        if new[i] == 'nomination':
                            nominations[y] = new[i-1]
                                
                        if new[i] == 'for':
                            bignominations[y] = new[i+1]
                                
                        
                    except:
                        print('Exception')
                        
            except:
                print('Exception')
                
        except:
            print('Exception')

        
        f.write(str(y)+'\t')
        f.write(str(n)+'\t')
        f.write(star.get(y)+ '\t'+oscars.get(y)+'\t'+str(another_Wins.get(y))+'\t'+str(nominations.get(y))+'\t'+str(bignominations.get(y))+'\n')
        y=y+1
    
    f.close()
    
    name = pd.DataFrame([name])  
    name = name.transpose()     
    rank = pd.DataFrame([star])
    rank = rank.transpose() 
    oscars = pd.DataFrame([oscars])
    oscars = oscars.transpose() 
    another_Wins = pd.DataFrame([another_Wins])
    another_Wins = another_Wins.transpose() 
    nominations = pd.DataFrame([nominations])
    nominations = nominations.transpose() 
    bignominations = pd.DataFrame([bignominations])
    bignominations = bignominations.transpose() 
     
    return name, rank, oscars, nominations, another_Wins, bignominations
    
    
####Function to divide actors, writers, directors into each column
def namecolumns(actor, writers, directors):
    x =0
    y =0
    z =0
    
    a1 = {}
    a2 = {}
    a3 = {}
    a4 = {}
    a5 = {}
    w1 = {}
    w2= {}
    d1 = {}
    d2 = {}
    for a in actor:
        #print(a)
        print(x)
        re.sub(r'[^\w]', '', a)
        a=a.strip().split(',')
        try:
            b = a[0].split('[')
            a1[x]= b[1]
        except:
            a1[x] = 'nan'
        try:
            a2[x] = a[1]
        except:
            a2[x] = 'nan'
        try:
            a3[x] = a[2]
        except:
            a3[x] = 'nan'
        try:
            a4[x] = a[3]
        except:
            a4[x] = 'nan'
        try:
            a5[x] = a[4]
        except:
            a5[x] = 'nan'
        x=x+1
    
    for w in writers:
        w=w.strip().split(',')
        try:
            w1[y]= w[0]
        except:
            w1[y] = 'nan'
        try:
            w2[y] = w[1]
        except:
            w2[y] = 'nan'
        y=y+1
    
    for d in directors:
        d=d.strip().split(',')
        try:
            d1[z]= d[0]
        except:
            d1[z] = 'nan'
        try:
            d2[z] = d[1]
        except:
            d2[z] = 'nan'
        z=z+1
   
    a1 = pd.DataFrame([a1])
    a2 = pd.DataFrame([a2])
    a3 = pd.DataFrame([a3])
    a4 = pd.DataFrame([a4])
    a5 = pd.DataFrame([a5])
    w1 = pd.DataFrame([w1])
    w2 = pd.DataFrame([w2])
    d1 = pd.DataFrame([d1])
    d2 = pd.DataFrame([d2])
    
    actors1 = pd.concat((a1,a2,a3,a4,a5), axis=0)
    writers1 = pd.concat((w1,w2), axis=0)
    directors1 = pd.concat((d1,d2), axis=0)
    actors=actors1.transpose()
    writers=writers1.transpose()
    directors=directors1.transpose()

    
    return  actors, writers, directors
    
###merging actors to their original formats
def finalmerge_actors(name_a,rank_a,oscars_a,nominations_a,another_wins_a,bignominations_a):

    x = -1
    
    imdb_actor1 = pd.DataFrame(columns=['actor1','actor1_star', 'actor1_oscars','actor1_nominations','actor1_otherWins','actor1_bignominations'])
    imdb_actor2 = pd.DataFrame(columns=['actor2','actor2_star', 'actor2_oscars','actor2_nominations','actor2_otherWins','actor2_bignominations'])
    imdb_actor3 = pd.DataFrame(columns=['actor3','actor3_star', 'actor3_oscars','actor3_nominations','actor3_otherWins','actor3_bignominations'])
    imdb_actor4 = pd.DataFrame(columns=['actor4','actor4_star', 'actor4_oscars','actor4_nominations','actor4_otherWins','actor4_bignominations' ])
    imdb_actor5 = pd.DataFrame(columns = ['actor5','actor5_star', 'actor5_oscars','actor5_nominations','actor5_otherWins','actor5_bignominations'])
    
    for i in imdb_new.loc[:,'actor1']:
        x=x+1
        a= -1
        for j in name_a:
            a=a+1
            if i == j:
                #x=x+1
                imdb_actor1.loc[x,'actor1'] = i
                imdb_actor1.loc[x,'actor1_star'] = rank_a[a]
                imdb_actor1.loc[x,'actor1_oscars'] = oscars_a[a]
                imdb_actor1.loc[x,'actor1_nominations'] = nominations_a[a]
                imdb_actor1.loc[x,'actor1_otherWins'] = another_wins_a[a]
                imdb_actor1.loc[x,'actor1_bignominations'] = bignominations_a[a]
    
          
    y= -1
    for i in imdb_new.loc[:,'actor2']:
        y=y+1
        b=-1
        for j in name_a:
            b = b+1
            if i == j:
                imdb_actor2.loc[y,'actor2'] = i
                imdb_actor2.loc[y,'actor2_star'] = rank_a[b]
                imdb_actor2.loc[y,'actor2_oscars'] = oscars_a[b]
                imdb_actor2.loc[y,'actor2_nominations'] = nominations_a[b]
                imdb_actor2.loc[y,'actor2_otherWins'] = another_wins_a[b]
                imdb_actor2.loc[y,'actor2_bignominations'] = bignominations_a[b]
                
                
    z= -1
    
    for i in imdb_new.loc[:,'actor3']:
        z=z+1
        c=-1
        for j in name_a:
            c = c+1
            if i == j:
                imdb_actor3.loc[z,'actor3'] = i
                imdb_actor3.loc[z,'actor3_star'] = rank_a[b]
                imdb_actor3.loc[z,'actor3_oscars'] = oscars_a[b]
                imdb_actor3.loc[z,'actor3_nominations'] = nominations_a[b]
                imdb_actor3.loc[z,'actor3_otherWins'] = another_wins_a[b]
                imdb_actor3.loc[z,'actor3_bignominations'] = bignominations_a[b]
                
                
    w= -1
    
    for i in imdb_new.loc[:,'actor4']:
        w=w+1
        d=-1
        for j in name_a:
            d = d+1
            if i == j:
                imdb_actor4.loc[w,'actor4'] = i
                imdb_actor4.loc[w,'actor4_star'] = rank_a[d]
                imdb_actor4.loc[w,'actor4_oscars'] = oscars_a[d]
                imdb_actor4.loc[w,'actor4_nominations'] = nominations_a[d]
                imdb_actor4.loc[w,'actor4_otherWins'] = another_wins_a[d]
                imdb_actor4.loc[w,'actor4_bignominations'] = bignominations_a[d]
                
    u= -1
    
    for i in imdb_new.loc[:,'actor5']:
        u=u+1
        e = -1
        for j in name_a:
            e = e+1
            if i == j:
                imdb_actor5.loc[u,'actor5'] = i
                imdb_actor5.loc[u,'actor5_star'] = rank_a[e]
                imdb_actor5.loc[u,'actor5_oscars'] = oscars_a[e]
                imdb_actor5.loc[u,'actor5_nominations'] = nominations_a[e]
                imdb_actor5.loc[u,'actor5_otherWins'] = another_wins_a[e]
                imdb_actor5.loc[u,'actor5_bignominations'] = bignominations_a[e]
                
    imdb_actor = pd.concat([imdb_actor1,imdb_actor2,imdb_actor3,imdb_actor4,imdb_actor5], axis=1)
            
    return imdb_actor


###merging directors information to their original format
def finalmerge_directors(name_d,rank_d,oscars_d,nominations_d,another_wins_d,bignominations_d):

    x = -1 
    imdb_director1 = pd.DataFrame()
    imdb_director1 = pd.DataFrame(columns=['director1','director2',
                                        'director1_star', 'director1_oscars','director1_nominations','director1_otherWins','director1_bignominations',
                                        'director2_star', 'director2_oscars','director2_nominations','director2_otherWins','director2_bignominations'])
    
    for i in imdb_new.loc[:,'director1']:
        x=x+1
        a= -1
        for j in name_d:
            a=a+1
            if i == j:
                #x=x+1
                imdb_director1.loc[x,'director1'] = i
                imdb_director1.loc[x,'director1_star'] = rank_d[a]
                imdb_director1.loc[x,'director1_oscars'] = oscars_d[a]
                imdb_director1.loc[x,'director1_nominations'] = nominations_d[a]
                imdb_director1.loc[x,'director1_otherWins'] = another_wins_d[a]
                imdb_director1.loc[x,'director1_bignominations'] = bignominations_d[a]
            

    y= -1
    for i in imdb_new.loc[:,'director2']:
        y=y+1
        b=-1
        for j in name_d:
            b = b+1
            if i == j:
                imdb_director1.loc[y,'director2'] = i
                imdb_director1.loc[y,'director2_star'] = rank_d[b]
                imdb_director1.loc[y,'director2_oscars'] = oscars_d[b]
                imdb_director1.loc[y,'director2_nominations'] = nominations_d[b]
                imdb_director1.loc[y,'director2_otherWins'] = another_wins_d[b]
                imdb_director1.loc[y,'director2_bignominations'] = bignominations_d[b]
     
    
               
    return imdb_director1


###merging writers information to thier original format
def finalmerge_writers(name_w,rank_w,oscars_w,nominations_w,another_wins_w,bignominations_w):

    x = -1 
    imdb_writer1 = pd.DataFrame()
    imdb_writer1 = pd.DataFrame(columns=['writer1','writer2',
                                        'writer1_star', 'writer1_oscars','writer1_nominations','writer1_otherWins','writer1_bignominations',
                                        'writer2_star', 'writer2_oscars','writer2_nominations','writer2_otherWins','writer2_bignominations'])
    
    for i in imdb_new.loc[:,'writer1']:
        x=x+1
        a= -1
        for j in name_w:
            a=a+1
            if i == j:
                #x=x+1
                imdb_writer1.loc[x,'writer1'] = i
                imdb_writer1.loc[x,'writer1_star'] = rank_w[a]
                imdb_writer1.loc[x,'writer1_oscars'] = oscars_w[a]
                imdb_writer1.loc[x,'writer1_nominations'] = nominations_w[a]
                imdb_writer1.loc[x,'writer1_otherWins'] = another_wins_w[a]
                imdb_writer1.loc[x,'writer1_bignominations'] = bignominations_w[a]
            

    y= -1
    for i in imdb_new.loc[:,'writer2']:
        y=y+1
        b=-1
        for j in name_w:
            b = b+1
            if i == j:
                imdb_writer1.loc[y,'writer2'] = i
                imdb_writer1.loc[y,'writer2_star'] = rank_w[b]
                imdb_writer1.loc[y,'writer2_oscars'] = oscars_w[b]
                imdb_writer1.loc[y,'writer2_nominations'] = nominations_w[b]
                imdb_writer1.loc[y,'writer2_otherWins'] = another_wins_w[b]
                imdb_writer1.loc[y,'writer2_bignominations'] = bignominations_w[b]
    
             
    return imdb_writer1

#******Run 1st- to divide names into each column***********
"""
actors, writers, directors = namecolumns(rt.loc[:,'actors'], rt.loc[:,'Written By'], rt.loc[:,'Directed By'])
consolidate = pd.concat((actors, writers, directors), axis=1)
consolidate.columns = ['actor1', 'actor2', 'actor3', 'actor4', 'actor5', 'writer1', 'writer2', 'director1', 'director2']
with open('imdb_awd.csv', 'a+') as imdb:
    consolidate.to_csv(imdb,  encoding='utf-8')
"""
imdb_new = pd.read_csv('imdb_awd.csv')
imdb_new.replace(r'\s+', np.nan, regex=True)


####Run 2nd- scrapes actor information from imdb and writes into out_actor.csv file. When program stops run file again
"""
###if program stops after 1st time comment below two lines and run file again
act_list = actorslist(imdb_new)
name_a, rank_a, oscars_a, nominations_a, another_wins_a, bignominations_a = actorstarmeter(act_list)


actor_final = pd.concat([name_a, rank_a, oscars_a, nominations_a, another_wins_a, bignominations_a],axis=1)
actor_final.columns = ['name_a', 'rank_a', 'oscars_a', 'nominations_a', 'another_wins_a', 'bignominations_a']


if os.path.exists('out_actor.csv'): 
    with open('out_actor.csv', 'a+') as act:
        actor_final.to_csv(act, header=False, na_rep = np.nan, encoding='utf-8')
else:
    with open('out_actor.csv', 'a+') as act:
        actor_final.to_csv(act, header=True, na_rep = np.nan, encoding='utf-8')
"""

###Run 3rd- scrapes writers information from imdb into out_writer.csv file. Run file if program stops
"""
###if program stops after 1st time comment below two lines and run file again
writer_list = writerslist(imdb_new)
name_w, rank_w, oscars_w, nominations_w, another_wins_w, bignominations_w  = writerstarmeter(writer_list)


writer_final = pd.concat([name_w, rank_w, oscars_w, nominations_w, another_wins_w, bignominations_w],axis=1)
writer_final.columns = ['name_w', 'rank_w', 'oscars_w', 'nominations_w', 'another_wins_w', 'bignominations_w']


if os.path.exists('out_writer.csv'): 
    with open('out_writer.csv', 'a+') as act:
        writer_final.to_csv(act, header=False, na_rep = np.nan, encoding='utf-8')
else:
    with open('out_writer.csv', 'a+') as act:
        writer_final.to_csv(act, header=True, na_rep = np.nan, encoding='utf-8')
"""


###Run 4th- scrapes directors information from imdb into out_director.csv file. Run file if program stops.
"""
###if program stops after 1st time comment below two lines and run file again
direct_list = directorslist(imdb_new)
name_d, rank_d, oscars_d, nominations_d, another_wins_d, bignominations_d = directorstarmeter(direct_list)


director_final = pd.concat([name_d, rank_d, oscars_d, nominations_d, another_wins_d, bignominations_d],axis=1)
director_final.columns = ['name_d', 'rank_d', 'oscars_d', 'nominations_d', 'another_wins_d', 'bignominations_d']


if os.path.exists('out_director.csv'): 
    with open('out_director.csv', 'a+') as act:
        director_final.to_csv(act, header=False, na_rep = np.nan, encoding='utf-8')
else:
    with open('out_director.csv', 'a+') as act:
        director_final.to_csv(act, header=True, na_rep = np.nan, encoding='utf-8')

"""

###Run 5th- reading data from out_* files into three dfs and outputs single final_imdb.csv file. Merges for all the rows.
#######Should run in one go
"""
out_actor = pd.read_csv('out_actor.csv')
out_writer = pd.read_csv('out_writer.csv')
out_director = pd.read_csv('out_director.csv')


imdb_actors = finalmerge_actors(out_actor.loc[:,'name_a'], out_actor.loc[:,'rank_a'],out_actor.loc[:,'oscars_a']
                    , out_actor.loc[:,'nominations_a'], out_actor.loc[:,'another_wins_a'], out_actor.loc[:,'bignominations_a'])


imdb_directors = finalmerge_directors(out_writer.loc[:,'name_w'], out_writer.loc[:,'rank_w'],out_writer.loc[:,'oscars_w'],
                 out_writer.loc[:,'nominations_w'], out_writer.loc[:,'another_wins_w'], out_writer.loc[:,'bignominations_w'])

imdb_writers = finalmerge_writers(out_director.loc[:,'name_d'], out_director.loc[:,'rank_d'],out_director.loc[:,'oscars_d']
                   , out_director.loc[:,'nominations_d'], out_writer.loc[:,'another_wins_d'], out_writer.loc[:,'bignominations_d'])

for i in range(len(imdb_new)):
        if i not in imdb_actors.index:
            imdb_actors.loc[i,:] = 'nan'
imdb_actors.sort_index(inplace=True)
         
for i in range(len(imdb_new)):
        if i not in imdb_writers.index:
            imdb_writers.loc[i,:] = 'nan'           
imdb_writers.sort_index(inplace=True)           
            
for i in range(len(imdb_new)):
        if i not in imdb_directors.index:
            imdb_directors.loc[i,:] = 'nan'
imdb_directors.sort_index(inplace=True)

final_imdb = pd.concat([imdb_actors, imdb_directors, imdb_writers],axis=1)

with open('final_imdb.csv', 'a+') as final:
        final_imdb.to_csv(final, header=True, na_rep = np.nan, encoding='utf-8')
"""
