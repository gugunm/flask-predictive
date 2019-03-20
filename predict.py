from sklearn.metrics import mean_squared_error
from math import sqrt
import pandas as pd
import numpy as np
import pickle
import json
import math
import os

def predict(dictModels, df2, dPrice):
  listResult = []
  for column in df2:
    modelName = dictModels[column]
    model = pickle.load(open('models/'+modelName,'rb'))
    predictions = model.predict(start=len(df2[column].values)-7, end=len(df2[column].values)-1)
    rmse = sqrt(mean_squared_error(df2[column][len(df2[column].values)-7:].values, predictions))
    if math.isinf(rmse):
      rmse = 0

    predictions = predictions.tolist()
    predictions = [0 if i < 0 else i for i in predictions]
    predictions = [math.floor(i) if i-math.floor(i) < 0.5 else math.ceil(i) for i in predictions]
    data = {
      "menu"        : column,
      "predictions" : predictions,
      "rmse"        : rmse
    }
    listResult.append(data)
  allData = {
    "data" : listResult
  }
  jsonData = json.dumps(allData)
  return jsonData

def forecast(dictModels, df2, dPrice):
  listResult = []
  allPrediction = []
  for column in df2:
    modelName = dictModels[column]
    model = pickle.load(open('models/'+modelName,'rb'))
    predictions = model.forecast(7)
    try:
      priceProduct = dPrice.loc[column, 'Price']
    except:
      priceProduct = 0

    predictions = predictions.tolist()
    predictions = [0 if i < 0 else i for i in predictions]
    predictions = [math.floor(i) if i-math.floor(i) < 0.5 else math.ceil(i) for i in predictions]
    data = {
      "menu"        : column,
      "predictions" : predictions,
      "price"       : int(priceProduct),
      "productRevenue"  : int(sum(predictions)*int(priceProduct))
    }

    listResult.append(data)
    allPrediction.append(predictions)

  allPrediction = sum(map(np.array, allPrediction))

  alldata = {
    "menu" : "ALL",
    "predictions" : allPrediction.tolist()
  }

  filterdata = {
    "data" : listResult
  }

  jsonfilter = json.dumps(filterdata)
  jsonall = json.dumps(alldata)
  return jsonfilter, jsonall

def totalsales(p):
  df = pd.DataFrame(p["data"]).set_index('menu')
  total = 0
  for index, row in df.iterrows():
    total += sum(row.values.tolist()[0])
  # print(total)
  data = {
    "totalSales" : int(total)
  }
  jsonData = json.dumps(data)
  return jsonData

def daySales(p):
  df = pd.DataFrame(p["data"]).set_index('menu')
  listSales = []
  for index, row in df.iterrows():
    listSales.append(row.values.tolist()[0])
  listSales = [ sum(row[i] for row in listSales) for i in range(len(listSales[0])) ]
  # print(listSales)
  data = {}
  for i, n in enumerate(listSales):
    data[i] = n
  jsonData = json.dumps(data)
  return jsonData

def totalrevenue(p):
  totalRevenue = 0
  for i in p["data"]:
    totalRevenue += i["totalPrice"]
  data = {
    "totalRevenue" : int(totalRevenue)
  }
  jsonData = json.dumps(data)
  return jsonData