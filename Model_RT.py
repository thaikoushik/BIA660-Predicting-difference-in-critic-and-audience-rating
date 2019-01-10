#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 21:05:36 2018

@author: SaiSanthosh
"""

import numpy as np
import pandas as pd
from fancyimpute import MICE
from sklearn import preprocessing, svm
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, LinearRegression, Lars, HuberRegressor,SGDRegressor, Ridge, BayesianRidge
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.grid_search import GridSearchCV
from sklearn.metrics.pairwise import chi2_kernel
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ExpSineSquared
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
import pickle
from sklearn.kernel_ridge import KernelRidge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score
from sklearn.preprocessing import normalize
#from mlxtend.regressor import StackingRegressor

final_df = pd.read_csv('UpdatedPerformance.csv', encoding='utf-8')

droplist = ['Studio','movie_id', 'Box Office', 'actor1', 'actor2', 'actor3', 'director1']

final_df = final_df.drop(droplist,axis=1)


X_corr = final_df.corr()

X = final_df.drop(['Unnamed: 0','Unnamed: 0.1','Classics','diff_rating','Special Interest','actor1_otherWins','actor2_otherWins','actor3_otherWins','director1_otherWins'],axis=1)
X_corr = X.corr()
X=X.round(0)

stars_col_list = ['actor1_star', 'actor2_star', 'actor3_star', 'director1_star']
for col in stars_col_list:
    X[col] = X[col] / X[col].max()
    
X['year'] = X['year'] - X['year'].min()
X['year'] = X['year'] / X['year'].max()
        
X = X.abs()

y_train= final_df['diff_rating']
X_train = X



lars = Lars()
lars_grid = [{'n_nonzero_coefs': [200, 400, 600]}]
lars_model1 = GridSearchCV(lars, lars_grid, cv =10, scoring = 'neg_mean_absolute_error')
lars_model2 = GridSearchCV(lars, lars_grid, cv =10, scoring = 'neg_mean_squared_error')
lars_model1.fit(X_train, y_train)
lars_model2.fit(X_train, y_train)
print("Mean Absolute Error:" , lars_model1.best_score_)
print("Mean Square Error:" , lars_model2.best_score_)
filename6 = 'lars_model1.sav'
pickle.dump(lars_model1, open(filename6,'wb'))

filename16 = 'lars_model2.sav'
pickle.dump(lars_model2, open(filename16,'wb'))


hreg = HuberRegressor()
hreg_grid = [{'epsilon': [1.5, 1.35, 1], 'max_iter':[200, 400, 600]}]
hreg_model1= GridSearchCV(hreg, hreg_grid, cv=10, scoring = 'neg_mean_absolute_error')
hreg_model2 = GridSearchCV(hreg, hreg_grid, cv=10, scoring =  'neg_mean_squared_error')
hreg_model1.fit(X_train, y_train)
hreg_model2.fit(X_train, y_train)
filename5 = 'hreg.sav'
pickle.dump(hreg_model1, open(filename5,'wb'))



kridge = KernelRidge()
kridge_grid=[{'alpha':[0.75, 0.25], 'kernel':['linear', 'polynomial']}]
kridge_model = GridSearchCV(kridge, kridge_grid, cv =10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
kridge_model.fit(X_train, y_train)
filename6 = 'kridge.sav'
pickle.dump(kridge_model, open(filename6,'wb'))



gbr = GradientBoostingRegressor()
gbr_grid = [{'loss':['ls', 'lad', 'quantile'], 'n_estimators' : [500,1000], 'max_depth' : [5,7]}]
gbr_model = GridSearchCV(gbr, gbr_grid, cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
gbr_model.fit(X_train, y_train)
filename4 = 'gbr.sav'
pickle.dump(gbr_model, open(filename4, 'wb'))



svr = svm.SVR()
svr_grid = [{'kernel':[ 'linear','poly', 'rbf', 'sigmoid']}]
svr_model = GridSearchCV(svr,svr_grid,cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
svr_model.fit(X_train, y_train)
filename7 = 'svr.sav'
pickle.dump(svr_model, open(filename7, 'wb'))

sgd = SGDRegressor()
sgd_grid=[{'loss':['squared_loss','huber'], 'penalty':['l2','l1','elasticnet']}]
sgd_model = GridSearchCV(sgd, sgd_grid, cv = 10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
sgd_model.fit(X_train,y_train)
filename = 'sgd.sav'
pickle.dump(sgd_model, open(filename, 'wb'))


knn = KNeighborsRegressor()
knn_grid = [{'n_neighbors':[3,5,7,11,13,17,19,23,47], 'weights':['uniform','distance']}]
knn_model = GridSearchCV(knn, knn_grid, cv =10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
knn_model.fit(X_train, y_train)
filename1 = 'knn.sav'
pickle.dump(knn_model, open(filename1, 'wb'))


gpr = GaussianProcessRegressor()
gpr_grid=[{'kernel':['WhiteKernel','RationalQuadratic','ExpSineSquared'] }]
gpr_model = GridSearchCV(gpr, gpr_grid, cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
gpr_model.fit(X_train, y_train)
filename2 = 'gpr.sav'
pickle.dump(gpr_model, open(filename2, 'wb'))


dtree = DecisionTreeRegressor()
dtree_grid=[{'max_depth':[3,5,7,9,11],'criterion':['mse','friedman_mse','mae']}]
dtree_model = GridSearchCV(dtree, dtree_grid, cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
dtree_model.fit(X_train, y_train)
filename3 = 'dtree.sav'
pickle.dump(dtree_model, open(filename3, 'wb'))



scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error']

lr = LinearRegression()
parameters = [{'fit_intercept':[True,False],'normalize':[True,False],'copy_X':[True,False]}]
grid = GridSearchCV(lr,parameters,cv=10, scoring = 'mean_absolute_error')
grid.fit(X_train,y_train)
filename7= "lr_grid.sav"
pickle.dump(grid, open(filename7,'wb'))



rid_reg = Ridge()
ridge_parameters={'alpha':[0.1, 1.0, 10.0]}
grid_rid= GridSearchCV(rid_reg,ridge_parameters,cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
grid_rid.fit(X_train, y_train)
filename8= "ridge_grid.sav"
pickle.dump(grid, open(filename8,'wb'))


la_reg = Lasso()
lasso__alpha = [0.1, 1.0, 10.0]
parameters={'alpha':lasso__alpha}
grid_la= GridSearchCV(la_reg,parameters,cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'])
grid_la.fit(X_train,y_train)
filename9= "lass_grid.sav"
pickle.dump(grid, open(filename9,'wb'))


ba_reg = BayesianRidge(compute_score = True)
ba_parameters = [{'n_iter': [300, 500,700]}]
ba_model =GridSearchCV(ba_reg, ba_parameters, cv=10, scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error'] )
ba_reg.fit(X_train, y_train)
filename10= "ba_reg.sav"
pickle.dump(ba_reg, open(filename10,'wb'))



