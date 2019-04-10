from sklearn.metrics import mean_squared_error
from datetime import date
from math import sqrt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import dateutil
import warnings
import math
import glob
import json
import sys
import os

import fetchData as fd

warnings.filterwarnings("ignore")

def coutMenu(df):
  arr_date = df['date'].unique().tolist()
  for i, dt in enumerate(arr_date):
    dt2 = df[df['date'] == dt]
    dt2 = dt2.iloc[:,1:]  
    dt2 = dt2.groupby(['productName'])["qty"].apply(lambda x : x.astype(int).sum())
    dt2 = dt2.reset_index()
    dt2 = dt2.fillna(method='ffill')
    
    dfDate = pd.DataFrame(dt, index=range(len(dt2.values)), columns=range(1))
    # return dfDate
    # dt2 = dt2.reset_index()
    dt2 = dt2.rename(columns={'qty': 'total', 'productName': 'menu'})
    dt2 = pd.concat([dfDate, dt2], axis=1)
    dt2 = dt2.rename(columns={0: 'Date'})
    if i == 0:
      df2 = dt2
    else:
      df2 = pd.concat([df2, dt2], ignore_index=True) #.append(dt2) #pd.concat([df2, dt2], axis=0)
  df2 = df2
  return df2

def transformDf(df):
  listMenu = df['menu'].unique().tolist()
  listDate = df['Date'].unique().tolist()

  dfMenu = pd.DataFrame(listMenu).rename(columns={0: 'menu'})
  dfDate = pd.DataFrame(0, index=np.arange(len(listMenu)), columns=listDate)
  
  df2 = pd.concat([dfMenu, dfDate], axis=1)
  df2 = df2.set_index(["menu"])

  for column in df2:
    oneDate = df[df['Date'] == column]
    oneDate = oneDate.iloc[:,1:].set_index('menu').T

    oneDateColumn = oneDate.columns.values.tolist()

    for i_menu, row in df2[column].iteritems():
      if i_menu in oneDateColumn:
        df2.loc[i_menu].at[column] = oneDate.iloc[0][i_menu]
  
  return df2.T

def arimaModel(df2, dPrice, scfg, n_test=None):
  listMenu = list()
  allPrediction = list()
  for column in df2:
    train = df2[column].values
    # check, is the product axis or no
    if column in scfg:
      # if the product axis, use parameter from the file
      cfg = scfg[column]
      p, d, q, P, D, Q, N, t, rmse = cfg["p"], cfg["d"], cfg["q"], cfg["P"], cfg["D"], cfg["Q"], cfg["N"], cfg["t"], cfg["rmse"] # sarimax.main(df2[column], n_test) 
    else:
      # if no axis, give the parameter like below
      p, d, q, P, D, Q, N, t, rmse = 0, 0, 0, 0, 0, 0, n_test, 'c', 0.0

    # ========= S A R I M A X ============
    mod = sm.tsa.statespace.SARIMAX(
      train, 
      order = (p,d,q), # 0,1,0
      seasonal_order = (P,D,Q,N), # 1,1,0,7
      enforce_stationarity=False,
      enforce_invertibility=False,
      trend = t)
    model_fit = mod.fit(maxiter=200, method='nm', disp=0)
    # ====================================

    # forecast as many as cfg["N"] > seasonal
    prediction = model_fit.forecast(N)
    
    try:
      priceProduct = dPrice.loc[column, 'price']
    except:
      priceProduct = 0

    prediction = prediction.tolist()
    prediction = [0 if i < 0 else i for i in prediction]
    prediction = [math.floor(i) if i-math.floor(i) < 0.5 else math.ceil(i) for i in prediction]

    data = {
      "menu"            : column,
      "predictions"     : prediction,
      "price"           : int(priceProduct),
      "productRevenue"  : int(sum(prediction)*int(priceProduct)),
      "rmse"            : rmse
    }

    listMenu.append(data)
    allPrediction.append(prediction)

  allPrediction = sum(map(np.array, allPrediction))
  dictSales = {
    "menu"        : "ALL",
    "predictions" : allPrediction.tolist()
  }

  return dictSales, listMenu

def totalsales(dataMenu):
  df = pd.DataFrame(dataMenu).set_index('menu')
  total = 0
  for index, row in df.iterrows():
    total += sum(row.values.tolist()[0])
  data = {
    "totalSales" : int(total)
  }
  return data

def totalrevenue(dataMenu):
  totalRevenue = 0
  for i in dataMenu:
    totalRevenue += i["productRevenue"]
  data = {
    "totalRevenue" : int(totalRevenue)
  }
  return data

def predictionCategory(df, dataMenu):
  listCategory = df["categoryName"].unique().tolist()
  dataCategory = list()
  for category in listCategory:
    dc = df[df["categoryName"] == category]
    listMenu = dc["productName"].unique().tolist()

    for no, menu in enumerate(listMenu):
      predMenu = [d["predictions"] for d in dataMenu if d['menu'] == menu]#[0]["predictions"]
      if no == 0:
        sumPredMenu = predMenu
      else:
        sumPredMenu = np.sum([sumPredMenu,predMenu], axis=0).tolist()

    dataCategory.append({
      "category" : category,
      "predictions" : sumPredMenu
    })
  
  return dataCategory

def processData(df, n_product=None):
  df = coutMenu(df)
  df2 = transformDf(df)

  if n_product:
    return df2.iloc[:,:n_product]
  return df2

def processAllData(df=None, dfPrice=None, fModel='models', fConfigs='configs', n_test=None, n_product=None):
  # take all company name from data
  list_company = df["companyId"].unique()
  # loop for every company
  for company in list_company:
    # load the configs json of the company to define the cfg deppands on the days
    dictConfigs = json.load(open(fConfigs+'/'+company+'.json','r'))
    # load the model json of the company to update the prediction deppands on the days
    dictModel = json.load(open(fModel+'/'+company+'.json','r'))

    # create dict for new prediction for the company deppands on the days
    dictCompany = dict()

    # initialization the cfg keys for the json file
    daysKeyCfg = str(n_test)+'daysConfig'
    # initialization the model keys for the json file
    daysKeyModel = str(n_test)+'daysModel'

    # if company doesn't has the predictions of the day, break it
    if daysKeyCfg not in dictConfigs:
      break
    # else, continue
    else:
      # get the cfg of the company, deppands on the day
      dictDays = dictConfigs[daysKeyCfg]
      
      # get the data of the company
      dfCompany = df[df["companyId"] == company]
      # get price data of the company
      priceComp = dfPrice[dfPrice["companyId"] == company]

      # get all store of each company
      list_store = dfCompany["storeId"].unique()
      # initialization list of all prediction for the company
      predCompany = list()
      # initialization list of all revenue from all store for the company
      revCompany = list()

      # loop for every store in the company
      for store in list_store:
        # get the store data of the company
        dfStore = dfCompany[dfCompany["storeId"] == store]
        # get the price store data of the company
        priceStore = priceComp[priceComp["storeId"] == store]
        # get the cfg of store model
        storeConfig= dictDays[store]

        # define the n_product that you want to process, if the n_product is None, mean all product will be process, df2 is the data of store
        df2 = processData(dfStore[["date", "productName", "qty"]], n_product)
        # df3 is the price data of the store
        df3 = priceStore[["name", "price"]].rename(columns={"name":"productName"}).set_index("productName")

        # this line is to modeling the data for every store. look the arimaModel func for details
        dictSales, dataMenu = arimaModel(df2, df3, storeConfig, n_test)

        # if you define n_product, mean there is no filter for product category
        if n_product:
          dataCategory = ' '
        # else, product will categorize
        else:
          dataCategory = predictionCategory(dfStore[["categoryName", "productName"]], dataMenu)

        # this line is for calculate the total sales of the store
        totalSales = totalsales(dataMenu)
        # this line is for calculate the total revenue of the store
        totalRevenue = totalrevenue(dataMenu)

        # initialization the obj for store of the company
        dictCompany[store] = {
          "sales" : dictSales,
          "dataMenu" : dataMenu,
          "dataCategory" : dataCategory,
          "totalSales" : totalSales,
          "totalRevenue" : totalRevenue
        }

        # append the dictsales to the prediction of company
        predCompany.append(dictSales["predictions"])
        # append the total revenue to the company revenue
        revCompany.append(totalRevenue["totalRevenue"])
        
      # sum the prediction of every store, and will produce for the company prediction
      predCompany = [sum(x) for x in zip(*predCompany)]
      # sum the revenue of every store, and will produce for the company revenue
      revCompany  = sum(revCompany)

      # initialize the obj of the company value
      dictCompany["allstore"] = {
        "store" : "ALL",
        "predictions" : predCompany,
        "revenue" : revCompany
      }

      # update the data of the company that existed before
      dictModel[daysKeyModel] = dictCompany

      # save the update model to the folder
      fileName = fModel+'/'+company+'.json'
      json.dump(dictModel, open(fileName,'w'))

def nBuildModel():
  # default parameter for fetchdatabase function
  # DATABASE_NAME='customer', USERNAME='postgres', PASSWORD='postgres', HOSTNAME='localhost', PORT='5432'
  dfall, dfPrice = fd.fetchdatabase()

  # take the n_test to predict model depands on n_test
  list_ntest = [3, 7, 14, 21, 30]

  for n_test in list_ntest:
    # process all data
    processAllData(df=dfall, dfPrice=dfPrice, fModel='models', fConfigs='configs', n_test=n_test)

  # load model and print it
  # d = json.load(open('models/aicollective.json','r'))
  # print(d)