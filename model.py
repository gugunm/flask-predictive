from sklearn.metrics import mean_squared_error
from datetime import date
from math import sqrt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import dateutil
import pickle
import math
import json

def getPrice(pathData):
  df = pd.read_csv(pathData)
  df = df[['Menu Name', 'Price']]
  df = df.drop_duplicates(keep='first')
  df = df[df['Price'] > 0]
  df = df.set_index('Menu Name')
  return df

def readData(pathData):
  df = pd.read_csv(pathData)
  df = df.iloc[:,:4]
  df = df.fillna(method='ffill')
  df['Date'] = df['Date'].apply(dateutil.parser.parse).dt.date
  df = df.iloc[:,:-1]
  return df

def coutMenu(df):
  uniqueDate = df['Date'].unique()
  arr_date = []
  for d in uniqueDate:
    arr_date.append(d)

  for i, dt in enumerate(arr_date):
    dt2 = df[df['Date'] == dt]
    dt2 = dt2.iloc[:,1:2]  
    dt2 = dt2['Menu Name'].value_counts()

    dfDate = pd.DataFrame(dt, index=range(len(dt2.values)), columns=range(1))
    dt2 = dt2.reset_index()
    dt2 = dt2.rename(columns={'Menu Name': 'total', 'index': 'menu'})
    dt2 = pd.concat([dfDate, dt2], axis=1)
    dt2 = dt2.rename(columns={0: 'Date'})
    if i == 0:
      df2 = dt2
    else:
      df2 = pd.concat([df2, dt2], ignore_index=True) #.append(dt2) #pd.concat([df2, dt2], axis=0)

  df2 = df2
  df2.head()
  return df2

def transformDf(df):
  listMenu = list(df['menu'].unique())
  listDate = list(df['Date'].unique())

  dfMenu = pd.DataFrame(listMenu)
  dfDate = pd.DataFrame(0, index=np.arange(len(listMenu)), columns=listDate)
  df2 = pd.concat([dfMenu, dfDate], axis=1)
  df2 = df2.rename(columns={0: 'menu'}).set_index('menu')

  for column in df2:
    oneDate = df[df['Date'] == column]
    oneDate = oneDate.iloc[:,1:].set_index('menu').T

    oneDateColumn = list(oneDate.columns.values)

    for i_menu, row in df2[column].iteritems():
      if i_menu in oneDateColumn:
        df2.loc[i_menu].at[column] = oneDate.iloc[0][i_menu]

  return df2.T

def arimaModel(df2, dPrice):
  listResult = []
  allPrediction = []
  for column in df2:
    sales_diff = df2[column].diff(periods=1)  # integreted order 1
    sales_diff = sales_diff[1:]
    
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
      priceProduct = dPrice.loc[column, 'Price']
    except:
      priceProduct = 0

    prediction = prediction.tolist()
    prediction = [0 if i < 0 else i for i in prediction]
    prediction = [math.floor(i) if i-math.floor(i) < 0.5 else math.ceil(i) for i in prediction]
    data = {
      "menu"        : column,
      "predictions" : prediction,
      "price"       : int(priceProduct),
      "productRevenue"  : int(sum(prediction)*int(priceProduct))
    }

    listResult.append(data)
    allPrediction.append(prediction)

  allPrediction = sum(map(np.array, allPrediction))
  alldata = {
    "menu" : "ALL",
    "predictions" : allPrediction.tolist()
  }
  filterdata = {
    "data" : listResult
  }

  fileName2 = 'models/'+str(date.today())+'dictAll'+'.pkl'
  fileName1 = 'models/'+str(date.today())+'dictFilter'+'.pkl'
  pickle.dump(filterdata, open(fileName1,'wb'))
  pickle.dump(alldata, open(fileName2,'wb'))

  return fileName1, fileName2

def arimaPredict(df): 
  models = [] 
  df2 = df.iloc[:len(df.index)-7 , :]
  for column in df2:
    # print('No. Product : ', column)
    sales_diff = df2[column].diff(periods=1)  # integreted order 1
    sales_diff = sales_diff[1:]
    
    train = df2[column].values
    # train = X[0:len(df2[column].values)-7]

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

    prediction = model_fit.predict(start=len(df[column].values)-7, end=len(df[column].values)-1) 
    rmse = sqrt(mean_squared_error(df[column][len(df[column].values)-7:].values, prediction))
    if math.isinf(rmse):
      rmse = 0

    prediction = prediction.tolist()
    prediction = [0 if i < 0 else i for i in prediction]
    prediction = [math.floor(i) if i-math.floor(i) < 0.5 else math.ceil(i) for i in prediction]
    data = {
      "menu"        : column,
      "prediction"  : prediction,
      "rmse"        : rmse
    }
    models.append(data)
  fileName = 'models/'+str(date.today())+'dictPredict'+'.pkl'
  pickle.dump(models, open(fileName,'wb'))
  return fileName

def proccessData(pathData):
  df = readData(pathData)
  df = coutMenu(df)
  df2 = transformDf(df)
  return df2