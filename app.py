from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from datetime import date
import fetchData as fd
import predict as pr
import model as md
import requests
import pickle
import json
import os

app = Flask(__name__)
api = Api(app)

pathData = 'data/dataset.csv' 

dfall, dfPrice = fd.fetchdatabase()
# print(type(dfall["companyId"].unique().tolist()))
# print(dfall.columns)

df = md.proccessData(pathData)
dPrice = md.getPrice(pathData)

listModels = os.listdir('models/') 

dictFilterName, dictAllName, dictPredictName = md.callModel(listModels, df, dPrice)
dataPred, dataAll = pr.forecast(dictFilterName, dictAllName)

class Sales(Resource):
    def get(self, companyId, storeId):
        # print(companyId, storeId)
        dictFilterName, dictAllName, dictPredictName = md.callModel(listModels, df, dPrice)
        dataPred, dataAll = pr.forecast(dictFilterName, dictAllName)
        try:
            if not request.args["menu"]:
                return jsonify({})
            elif request.args["menu"]:
                arg1 = request.args["menu"]
                # results = [d for d in data["data"] if arg1 in d['menu'] ]
                results = [d for d in dataPred["data"] if d['menu'] == arg1 ]
                if not results:
                    return jsonify({})
                return jsonify(results[0])
        except:
            return jsonify(dataAll)

class TotalSales(Resource):
    def get(self, companyId, storeId):
        total = pr.totalsales(dataPred)
        data2 = json.loads(total)
        return jsonify(data2)

class TotalRevenue(Resource):
    def get(self, companyId, storeId):
        totalRevenue = pr.totalrevenue(dataPred)
        data3 = json.loads(totalRevenue)
        return jsonify(data3)

class Predictive(Resource):
    def get(self, companyId, storeId):
        marginError = pr.predict(dictPredictName)
        data4 = json.loads(marginError)
        return jsonify(data4)

api.add_resource(Sales, '/api/<companyId>/<storeId>/sales')
api.add_resource(TotalSales, '/api/<companyId>/<storeId>/totalSales')
api.add_resource(TotalRevenue, '/api/<companyId>/<storeId>/totalRevenue')
api.add_resource(Predictive, '/api/<companyId>/<storeId>/predictive')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8123') 