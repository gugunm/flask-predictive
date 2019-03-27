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
import dummy_model as dm

app = Flask(__name__)
api = Api(app)

dfall, dfPrice = fd.fetchdatabase()
dm.processAllData(dfall, dfPrice)

class Sales(Resource):
    def get(self, companyId, storeId):
        dc = pickle.load(open('model/'+companyId+'.pkl','rb'))
        ds = dc[storeId]

        args = request.args.to_dict()

        try:
            if not args:
                return jsonify({})
            else:
                try :
                    results = [d for d in ds["dataMenu"] if d['menu'] == args["menu"] ]
                    if not results:
                        return jsonify({})
                    return jsonify(results[0])
                except:
                    results = [d for d in ds["dataCategory"] if d['category'] == args["category"] ]
                    if not results:
                        return jsonify({})
                    return jsonify(results[0])
        except:
            return jsonify(ds["sales"])

class TotalSales(Resource):
    def get(self, companyId, storeId):
        dc = pickle.load(open('model/'+companyId+'.pkl','rb'))
        ds = dc[storeId]

        return jsonify(ds["totalSales"])

class TotalRevenue(Resource):
    def get(self, companyId, storeId):
        dc = pickle.load(open('model/'+companyId+'.pkl','rb'))
        ds = dc[storeId]

        return jsonify(ds["totalRevenue"])

# class Predictive(Resource):
#     def get(self, companyId, storeId):
#         marginError = pr.predict(dictPredictName)
#         data4 = json.loads(marginError)
#         return jsonify(data4)

api.add_resource(Sales, '/api/<companyId>/<storeId>/sales')
api.add_resource(TotalSales, '/api/<companyId>/<storeId>/totalSales')
api.add_resource(TotalRevenue, '/api/<companyId>/<storeId>/totalRevenue')
# api.add_resource(Predictive, '/api/<companyId>/<storeId>/predictive')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8123') 