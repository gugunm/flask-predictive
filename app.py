from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from datetime import date
import fetchData as fd
import model as md
import warnings
import requests
import pickle
import json
import os

warnings.filterwarnings("ignore", category=FutureWarning)
app = Flask(__name__)
api = Api(app)

folderModel = 'models'

# dfall, dfPrice = fd.fetchdatabase()
# md.processAllData(dfall, dfPrice, folderModel)

class AllStore(Resource):
    def get(self, companyId):
        dc = pickle.load(open(folderModel+'/'+companyId+'.pkl','rb'))

        return jsonify(dc["allstore"])

class Sales(Resource):
    def get(self, companyId):
        dc = pickle.load(open(folderModel+'/'+companyId+'.pkl','rb'))
        args = request.args.to_dict()
        
        if not args:
            return jsonify({})
        try:
            if not args["storeId"]:
                return jsonify({})
            else:
                if not dc[args["storeId"]]:
                    return jsonify({})
                else:
                    ds = dc[args["storeId"]]
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
            return jsonify({})

class TotalSales(Resource):
    def get(self, companyId):
        dc = pickle.load(open(folderModel+'/'+companyId+'.pkl','rb'))
        args = request.args.to_dict()
        
        if not args:
            return jsonify({})
        try:
            if not args["storeId"]:
                return jsonify({})
            else:
                if not dc[args["storeId"]]:
                    return jsonify({})
                else:
                    ds = dc[args["storeId"]]                  
                    return jsonify(ds["totalSales"])
        except:
            return jsonify({})

class TotalRevenue(Resource):
    def get(self, companyId):
        dc = pickle.load(open(folderModel+'/'+companyId+'.pkl','rb'))
        args = request.args.to_dict()
        
        if not args:
            return jsonify({})
        try:
            if not args["storeId"]:
                return jsonify({})
            else:
                if not dc[args["storeId"]]:
                    return jsonify({})
                else:
                    ds = dc[args["storeId"]]                  
                    return jsonify(ds["totalRevenue"])
        except:
            return jsonify({})      

api.add_resource(AllStore, '/api/<companyId>')
api.add_resource(Sales, '/api/<companyId>/sales')
api.add_resource(TotalSales, '/api/<companyId>/totalSales')
api.add_resource(TotalRevenue, '/api/<companyId>/totalRevenue')

if __name__ == '__main__':
    dfall, dfPrice = fd.fetchdatabase()
    md.processAllData(dfall, dfPrice, folderModel)
    app.run(debug=True, host='0.0.0.0', port='5003', use_reloader=False) 