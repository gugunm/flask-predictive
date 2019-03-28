from sklearn.metrics import mean_squared_error
from datetime import date
from math import sqrt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import dateutil
import pickle
import math
import glob
import json
import os
import fetchData as fd

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

def arimaModel(df2, dPrice):
  listMenu = []
  allPrediction = []
  for column in df2:
    sales_diff = df2[column].diff(periods=1)  # integreted order 1
    sales_diff = sales_diff[1:]
    
    # train = sales_diff.values
    train = df2[column].values

    # ========= S A R I M A X ============
    mod = sm.tsa.statespace.SARIMAX(
      train, 
      order=(0,1,1), # 0,1,0
      seasonal_order=(0,1,0,7), # 1,1,0,7
      enforce_stationarity=False,
      enforce_invertibility=False,
      trend='c')
    model_fit = mod.fit(disp=0)
    # ====================================

    prediction = model_fit.forecast(7)
    
    try:
      priceProduct = dPrice.loc[column, 'price']
    except:
      priceProduct = 0

    prediction = prediction.tolist()
    prediction = [0 if i < 0 else i for i in prediction]
    prediction = [math.floor(i) if i-math.floor(i) < 0.5 else math.ceil(i) for i in prediction]
    rmse  = arimaPredict(df2[column]) 

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

def arimaPredict(df): 
  sales_diff = df.diff(periods=1)  # integreted order 1
  sd = sales_diff[1:]

  # train = sd[:len(sd.values)-7].values.tolist()
  # test  = sd[len(sd.values)-7:].values.tolist()
  train = df[:len(df.values)-7].values.tolist()
  test  = df[len(df.values)-7:].values.tolist()

  # ========= S A R I M A X ============
  mod = sm.tsa.statespace.SARIMAX( 
    train, 
    order=(0,1,1), # 0,1,0 
    seasonal_order=(0,1,0,7), # 1,1,0,7 
    enforce_stationarity=False,
    enforce_invertibility=False,
    trend='c')
  model_fit = mod.fit(disp=0)
  # ====================================

  prediction = model_fit.predict(start=len(sd.values)-7, end=len(sd.values)-1) 
  rmse = sqrt(mean_squared_error(test, prediction))
  if math.isinf(rmse):
    rmse = 0
  return rmse

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
  dataCategory = []
  for category in listCategory:
    dc = df[df["categoryName"] == category]
    listMenu = dc["productName"].unique().tolist()

    for no, menu in enumerate(listMenu):
      predMenu = [d for d in dataMenu if d['menu'] == menu][0]["predictions"]
      if no == 0:
        sumPredMenu = predMenu
      else:
        sumPredMenu = np.sum([sumPredMenu,predMenu], axis=0).tolist()

    dataCategory.append({
      "category" : category,
      "predictions" : sumPredMenu
    })
  
  return dataCategory

def processData(df):
  df = coutMenu(df)
  df2 = transformDf(df)

  return df2

def processAllData(df, dfPrice, fModel):
  files = glob.glob(fModel+'/*') 
  for f in files:
    os.remove(f)
  list_company = df["companyId"].unique()
  for company in list_company:
    dictCompany = {}
    
    dfCompany = df[df["companyId"] == company]
    priceComp = dfPrice[dfPrice["companyId"] == company]

    list_store = dfCompany["storeId"].unique()
    predCompany = []
    revCompany = []

    for store in list_store:
      dfStore = dfCompany[dfCompany["storeId"] == store]
      priceStore = priceComp[priceComp["storeId"] == store]

      df2 = processData(dfStore[["date", "productName", "qty"]])
      df3 = priceStore[["name", "price"]].rename(columns={"name":"productName"}).set_index("productName")

      dictSales, dataMenu = arimaModel(df2, df3)
      dataCategory = predictionCategory(dfStore[["categoryName", "productName"]], dataMenu)

      totalSales = totalsales(dataMenu)
      totalRevenue = totalrevenue(dataMenu)

      dictCompany[store] = {
        "sales" : dictSales,
        "dataMenu" : dataMenu,
        "dataCategory" : dataCategory,
        "totalSales" : totalSales,
        "totalRevenue" : totalRevenue
      }

      predCompany.append(dictSales["predictions"])
      revCompany.append(totalRevenue["totalRevenue"])
      
    predCompany = [sum(x) for x in zip(*predCompany)]
    revCompany  = sum(revCompany)

    dictCompany["allstore"] = {
      "store" : "ALL",
      "predictions" : predCompany,
      "revenue" : revCompany
    }

    fileName = fModel+'/'+company+'.pkl'
    pickle.dump(dictCompany, open(fileName,'wb'))
    
    
# dfall, dfPrice = fd.fetchdatabase()
# processAllData(dfall, dfPrice, 'models')
# d = pickle.load(open('models/aicollective.pkl','rb'))
# print(d["allstore"])

