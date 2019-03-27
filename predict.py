import pandas as pd
import pickle
import json

def predict(fileName):
  dictPredict = pickle.load(open(fileName,'rb'))
  jsonData = json.dumps(dictPredict)
  return jsonData

def forecast(fileName1, fileName2):
  dictFilter = pickle.load(open(fileName1,'rb'))
  dictAll = pickle.load(open(fileName2,'rb'))

  jsonall = dictAll #json.dumps(dictAll)
  jsonfilter = dictFilter #json.dumps(dictFilter)
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
    totalRevenue += i["productRevenue"]
  data = {
    "totalRevenue" : int(totalRevenue)
  }
  jsonData = json.dumps(data)
  return jsonData
