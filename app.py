from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from datetime import date, timedelta
import predict as pr
import model as md
import requests
import pickle
import json
import glob
import os
from pandas import DataFrame

app = Flask(__name__)
api = Api(app)

pathData = 'data/dataset.csv'
df = md.proccessData(pathData)

listModels = os.listdir('models/') 

if (len(listModels) == 0):
    md.arimaModel(df) 
elif (listModels[0][:10] != str(date.today())):
    files = glob.glob('models/*') 
    for f in files:
        os.remove(f)
    md.arimaModel(df) 

dictModels = pickle.load(open('models/dictModels.pkl','rb'))

class Predictive(Resource):
    def get(self):
        data = pr.forecast(dictModels, df)
        # data = pr.predict(dictModels, df)
        data = json.loads(data)
        
        try:
            arg1 = request.args["menu"]
            results = [d for d in data["data"] if arg1 in d['menu'] ]
            print(type(results))
            return jsonify(results)
        except:
            return jsonify(data)

api.add_resource(Predictive, '/api/predictive')

if __name__ == '__main__':
    app.run(port=8000, debug=True)