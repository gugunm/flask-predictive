from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from datetime import date
import predict as pr
import model as md
import requests
import pickle
import json
import glob
import os

app = Flask(__name__)
api = Api(app)

pathData = 'data/dataset.csv'
df = md.proccessData(pathData)
dPrice = md.getPrice(pathData)

listModels = os.listdir('models/') 

if (len(listModels) == 0):
    dictFilterName, dictAllName = md.arimaModel(df, dPrice) 
    dictPredictName = md.arimaPredict(df)
elif (listModels[0][:10] != str(date.today())):
    files = glob.glob('models/*') 
    for f in files:
        os.remove(f)
    dictFilterName, dictAllName = md.arimaModel(df, dPrice) 
    dictPredictName = md.arimaPredict(df)
else:
    dictAllName = 'models/'+str(date.today())+'dictAll'+'.pkl'
    dictFilterName = 'models/'+str(date.today())+'dictFilter'+'.pkl'
    dictPredictName = 'models/'+str(date.today())+'dictPredict'+'.pkl'

predictions, dataAll = pr.forecast(dictFilterName, dictAllName)
data = json.loads(predictions)

class Sales(Resource):
    def get(self):
        data1 = json.loads(dataAll)
        try:
            if not request.args["menu"]:
                return jsonify({})
            elif request.args["menu"]:
                arg1 = request.args["menu"]
                # results = [d for d in data["data"] if arg1 in d['menu'] ]
                results = [d for d in data["data"] if d['menu'] == arg1 ]
                if not results:
                    return jsonify({})
                return jsonify(results[0])
        except:
            return jsonify(data1)

class TotalSales(Resource):
    def get(self):
        total = pr.totalsales(data)
        data2 = json.loads(total)
        return jsonify(data2)

class TotalRevenue(Resource):
    def get(self):
        totalRevenue = pr.totalrevenue(data)
        data3 = json.loads(totalRevenue)
        return jsonify(data3)

class Predictive(Resource):
    def get(self):
        marginError = pr.predict(dictPredictName)
        data4 = json.loads(marginError)
        return jsonify(data4)

api.add_resource(Sales, '/api/sales')
api.add_resource(TotalSales, '/api/totalSales')
api.add_resource(TotalRevenue, '/api/totalRevenue')
api.add_resource(Predictive, '/api/predictive')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 