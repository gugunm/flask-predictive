from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from datetime import date
import requests
import warnings
import json
import os

warnings.filterwarnings("ignore")
app = Flask(__name__)
api = Api(app) 

folderModel = 'models'

class AllStore(Resource):
    def get(self, companyId):
        dc = json.load(open(folderModel+'/'+companyId+'.json','r'))
        args = request.args.to_dict()
        dd = dc[str(7)+"daysModel"]
        try:
            days = args["days"]
            dd = dc[days+"daysModel"]
        except:
            pass
        return jsonify(dd["allstore"])

class Sales(Resource):
    def get(self, companyId):
        dc = json.load(open(folderModel+'/'+companyId+'.json','r'))
        args = request.args.to_dict()
        dd = dc[str(7)+"daysModel"]
        if 'days' in args:
            try:
                days = args["days"]
                dd = dc[days+"daysModel"]
            except:
                return jsonify({"message" : "there is no prediction"})
        else:
            pass

        try:
            ds = dd[args["storeId"]]
            try:
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
        except:
            return jsonify({"message" : "there is no prediction"})

class TotalSales(Resource):
    def get(self, companyId):
        dc = json.load(open(folderModel+'/'+companyId+'.json','r'))
        args = request.args.to_dict()
        dd = dc[str(7)+"daysModel"]
        if 'days' in args:
            try:
                days = args["days"]
                dd = dc[days+"daysModel"]
            except:
                return jsonify({"message" : "there is no prediction"})
        else:
            pass

        try:
            ds = dd[args["storeId"]]                  
            return jsonify(ds["totalSales"])
        except:
            return jsonify({"message" : "there is no prediction"})

class TotalRevenue(Resource):
    def get(self, companyId):
        dc = json.load(open(folderModel+'/'+companyId+'.json','r'))
        args = request.args.to_dict()
        dd = dc[str(7)+"daysModel"]
        if 'days' in args:
            try:
                days = args["days"]
                dd = dc[days+"daysModel"]
            except:
                return jsonify({"message" : "there is no prediction"})
        else:
            pass

        try:
            ds = dd[args["storeId"]]                  
            return jsonify(ds["totalRevenue"])
        except:
            return jsonify({"message" : "there is no prediction"})

# example url http://0.0.0.0:8123/api/aicollective/sales?storeId=id_store & days=7 & menu=JAPANESE OCHA

api.add_resource(AllStore, '/api/<companyId>')
api.add_resource(Sales, '/api/<companyId>/sales')
api.add_resource(TotalSales, '/api/<companyId>/totalSales')
api.add_resource(TotalRevenue, '/api/<companyId>/totalRevenue')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 