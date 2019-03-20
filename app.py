from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from datetime import date, timedelta
import json
import predict as pr
import model as md
import requests
import pickle
import glob
import os
from pandas import DataFrame

app = Flask(__name__)
api = Api(app)

pathData = 'data/dataset.csv'
df = md.proccessData(pathData)
dPrice = md.getPrice(pathData)

listModels = os.listdir('models/') 

if (len(listModels) == 0):
    md.arimaModel(df) 
elif (listModels[0][:10] != str(date.today())):
    files = glob.glob('models/*') 
    for f in files:
        os.remove(f)
    md.arimaModel(df) 

dictModels = pickle.load(open('models/dictModels.pkl','rb'))
predictions, dataAll = pr.forecast(dictModels, df, dPrice)
data = json.loads(predictions)

class Sales(Resource):
    def get(self):
        # data = pr.forecast(dictModels, df)
        # data = pr.predict(dictModels, df)
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

class DaySales(Resource):
    def get(self):
        daySales = pr.daySales(data)
        data3 = json.loads(daySales)
        return jsonify(data3)

class TotalRevenue(Resource):
    def get(self):
        totalRevenue = pr.totalrevenue(data)
        data4 = json.loads(totalRevenue)
        return jsonify(data4)

api.add_resource(Sales, '/api/sales')
api.add_resource(TotalSales, '/api/totalSales')
api.add_resource(DaySales, '/api/daySales')
api.add_resource(TotalRevenue, '/api/totalRevenue')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')