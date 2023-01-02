# -*- coding: utf-8 -*-
"""yahoo_movie_user-gitipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-HvVyOu7lzRB5m0J_WoznFz-ENLHnGWm
"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive

drive.mount('/content/gdrive/', force_remount=True)
# %cd gdrive
# %cd MyDrive
# %cd Colab Notebooks
# %cd Rec_final
# %cd MLP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import missingno as msno
import seaborn as sns
from scipy.stats import norm, skew 
from scipy import stats
from datetime import datetime
import scipy.stats
import time
from pre_process import _preprocess_data
from reduce_size_df import reduce_mem_usage

df=pd.read_csv(r'ydata-ymovies-user-movie-ratings-train-v1_0.txt.gz',sep='\t',compression='gzip',encoding='latin-1',header=None)
df_test=pd.read_csv(r'ydata-ymovies-user-movie-ratings-test-v1_0.txt.gz',sep='\t',compression='gzip',encoding='latin-1',header=None)
df1=reduce_mem_usage(df)
df_test1=reduce_mem_usage(df_test)
df.rename(columns={0: 'u_id', 1: 'i_id',3:'rating'},inplace=True)
df.drop(2,axis='columns',inplace=True)
df_test.rename(columns={0: 'u_id', 1: 'i_id',3:'rating'},inplace=True)
df_test.drop(2,axis='columns',inplace=True)

"""
def validation_rmse_n(global_mean1,b_user,b_item,P,V,test_data,user_map,item_map):
    error=[]
    test_globalmean=test_data[:,2].sum()/test_data.shape[0]
    for i in range(test_data.shape[0]):
        user,item,rating= user_map[test_data[i,0]],item_map[test_data[i,1]],int(test_data[i,2])
        pred=test_globalmean+b_user[user]+b_item[item]+np.dot(P[user,:],V[:,item])
        error.append(rating-pred)
    residuals=np.array(error)
    loss= np.square(residuals).mean()
    rmse =loss
    return rmse

def training_rmse_n(global_mean1,b_user,b_item,P,V,training_data,user_map,item_map):
    error=[]
    for i in range(training_data.shape[0]):
        user,item,rating= training_data[i,0],training_data[i,1],training_data[i,2]
        pred=global_mean1+b_user[user]+b_item[item]+np.dot(P[user,:],V[:,item])
        error.append(rating-pred)
    residuals=np.array(error)
    loss= np.square(residuals).mean()
    rmse = loss
    return rmse

class rec():
    def __init__(self,train,learning_rate,features,beta,iterations,test,max_rating,min_rating):
        self.training_data,self.user_map,self.item_map=_preprocess_data(train)
        self.test=np.array(df_test)
        users_count = len(np.unique(self.training_data[:, 0]))
        items_count = len(np.unique(self.training_data[:, 1]))
        self.b_user = np.zeros(users_count)
        self.b_item = np.zeros(items_count)
        self.features=features
        self.learning_rate=learning_rate
        self.iterations=iterations
        self.beta=beta
        self.P=np.random.normal(0,0.1,(users_count, self.features))
        self.V=np.random.normal(0,0.1,(self.features,items_count))
        self.b=self.training_data[:,2].sum()/self.training_data.shape[0]
        self.max_rating=max_rating
        self.min_rating=min_rating
    
    def run_sgd(self):

        np.random.shuffle(self.training_data)
        for i in range(self.training_data.shape[0]):
            user,item,rating=int(self.training_data[i,0]),int(self.training_data[i,1]),int(self.training_data[i,2])
            pred_rating=self.b+self.b_user[user]+self.b_item[item] + np.dot(self.P[user,:],self.V[:,item])
            error = rating - pred_rating
            old_user=self.b_user[user]
            old_item=self.b_item[item]
            self.b_user[user]=self.b_user[user]+self.learning_rate*(error - self.beta*old_user)
            self.b_item[item]=self.b_item[item]+self.learning_rate*(error - self.beta*old_item)

            #lasso regularization l2

            old_pi=self.P[user,:]
            old_vi=self.V[:,item]
            self.P[user,:]=self.P[user,:]+self.learning_rate*(error*old_vi - self.beta*old_pi)
            self.V[:,item]=self.V[:,item]+self.learning_rate*(error*old_pi - self.beta*old_vi)

    def train(self):
        for i in range(self.iterations):
            start = time.time()
            self.run_sgd()
            if (i+1) % 1 == 0:
                val_rmse=validation_rmse_n(self.b,self.b_user,self.b_item,self.P,self.V,self.test,self.user_map,self.item_map)
                train_rmse=training_rmse_n(self.b,self.b_user,self.b_item,self.P,self.V,self.training_data,self.user_map,self.item_map)                
                end = time.time()
                print("Iteration: %d ;train_MSE =%.4f ;  val_MSE = %.4f ; time=%.4f" % (i+1,train_rmse, val_rmse,(end-start)))
                
                
    def full_matrix(self):
        return self.b + self.b_user.reshape(-1,1) + self.b_item.reshape(1,-1)+ np.dot(self.P,self.V)
    
    
    def clip_predict(self,actual_Rat):
        if actual_Rat>self.max_rating:
            pred=self.max_rating
        else:
            pred=self.actual_Rat
        if actual_Rat<self.min_rating:
            pred=self.min_rating
        else:
            pred=actual_Rat
        return pred

    def predict_user_movie(self,data_type,dataframe,user,item,clip=True):
        if data_type=='test':
            s=np.array(dataframe)
            test_globalmean=s[:,2].sum()/s.shape[0]
            if user in self.user_map and item in self.item_map:   
                user1,item1=self.user_map[user],self.item_map[item]
                self.actual_Rat=test_globalmean+ self.b_user[user1]+ self.b_item[item1]+np.dot(self.P[user1,:],self.V[:,item1])
                if clip is True:
                    return self.clip_predict(self.actual_Rat)
            else:
                print('user or item not known, the avg rating is')
                return test_globalmean
        elif data_type=='train':
                user1,item1=self.user_map[user],self.item_map[item]
                self.actual_Rat= self.b+ self.b_user[user1]+ self.b_item[item1]+np.dot(self.P[user1,:],self.V[:,item1])
                if clip is True:
                    return self.clip_predict(self.actual_Rat)

            
    
    def predict_dataset(self,dataframe):
            rating=[]
            d=np.array(dataframe)
            for i in d.shape[0]:
                user,item=d[i,0].d[i,2]
                rating.append(self.predict_user_movie('test',dataframe,user,item,clip=True))
                """

def validation_rmse(globalmean,P,V,test_data,user_map,item_map):
    error=[]
    for i in range(test_data.shape[0]):
        user,item,rating= user_map[test_data[i,0]],item_map[test_data[i,1]],int(test_data[i,2])
        pred=np.dot(P[user,:],V[:,item])
        error.append(rating-pred)
    residuals=np.array(error)
    loss= np.square(residuals).mean()
    rmse =loss
    return rmse

def training_rmse(globalmean,P,V,training_data,user_map,item_map):
    error=[]
    for i in range(training_data.shape[0]):
        user,item,rating= training_data[i,0],training_data[i,1],training_data[i,2]
        pred= np.dot(P[user,:],V[:,item])
        error.append(rating-pred)
    residuals=np.array(error)
    loss= np.square(residuals).mean()
    rmse = loss
    return rmse

class vanillarec():
    def __init__(self,train,learning_rate,features,iterations,test,max_rating,min_rating):
        self.training_data,self.user_map,self.item_map=_preprocess_data(train)
        self.test=np.array(df_test)
        self.training_data=np.array(self.training_data)
        users_count = len(np.unique(self.training_data[:, 0]))
        items_count = len(np.unique(self.training_data[:, 1]))
        self.features=features
        self.learning_rate=learning_rate
        self.iterations=iterations
        self.P=np.random.normal(0,0.1,(users_count, self.features))
        self.V=np.random.normal(0,0.1,(self.features,items_count))
        self.max_rating=max_rating
        self.min_rating=min_rating
        self.b=self.training_data[:,2].sum()/self.training_data.shape[0]
    
    def run_sgd(self):

        np.random.shuffle(self.training_data)
        for i in range(self.training_data.shape[0]):
            user,item,rating=int(self.training_data[i,0]),int(self.training_data[i,1]),int(self.training_data[i,2])
            pred_rating= np.dot(self.P[user,:],self.V[:,item])
            error = rating - pred_rating

            #lasso regularization l2

            old_pi=self.P[user,:]
            old_vi=self.V[:,item]
            self.P[user,:]=self.P[user,:]+self.learning_rate*(error*old_vi)
            self.V[:,item]=self.V[:,item]+self.learning_rate*(error*old_pi )

    def train(self):
        self.trainloss=[]
        self.valloss=[]
        for i in range(self.iterations):
            start = time.time()
            self.run_sgd()
            if (i+1) % 1 == 0:
                val_mse=validation_rmse(self.b,self.P,self.V,self.test,self.user_map,self.item_map)
                self.valloss.append(val_mse)
                train_mse=training_rmse(self.b,self.P,self.V,self.training_data,self.user_map,self.item_map)                
                self.trainloss.append(train_mse)
                end = time.time()
                print("Iteration: %d ;train_MSE =%.4f ;  val_MSE = %.4f ; time=%.4f" % (i+1,train_mse, val_mse,(end-start)))
                plt.plot(self.valloss,label='val_loss')
                plt.plot(self.trainloss,color='blue',label='train_loss')
                plt.xlabel('epochs')
                plt.ylabel('MSE')
                #plt.legend()
             
    def full_matrix(self):
        return self.b + np.dot(self.P,self.V)
    
    def clip_predict(self,actual_Rat):
        if actual_Rat>self.max_rating:
            pred=self.max_rating
        else:
            pred=self.actual_Rat
        if actual_Rat<self.min_rating:
            pred=self.min_rating
        else:
            pred=actual_Rat
        return pred
    def predict_user_movie(self,data_type,dataframe,user,item,clip=True):
        if data_type=='test':
            s=np.array(dataframe)
            test_globalmean=s[:,2].sum()/s.shape[0]
            if user in self.user_map and item in self.item_map:   
                user1,item1=self.user_map[user],self.item_map[item]
                self.actual_Rat=test_globalmean+ self.b_user[user1]+ self.b_item[item1]+np.dot(self.P[user1,:],self.V[:,item1])
                if clip is True:
                    return self.clip_predict(self.actual_Rat)
            else:
                print('user or item not known, the avg rating is')
                return test_globalmean
        elif data_type=='train':
                user1,item1=self.user_map[user],self.item_map[item]
                self.actual_Rat= self.b+ self.b_user[user1]+ self.b_item[item1]+np.dot(self.P[user1,:],self.V[:,item1])
                if clip is True:
                    return self.clip_predict(self.actual_Rat)
    def predict_dataset(self,dataframe):
            rating=[]
            d=np.array(dataframe)
            for i in d.shape[0]:
                user,item=d[i,0].d[i,2]
                rating.append(self.predict_user_movie('test',dataframe,user,item,clip=True))

Rec_v=vanillarec(train=df,  learning_rate=0.001,  features=15,iterations=400,test=df_test,
       max_rating=5,min_rating=1)
Rec_v.train()