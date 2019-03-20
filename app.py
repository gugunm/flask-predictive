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
        data = json.loads(data)
        return jsonify(data)

class PredictiveOne(Resource):
    def get(self, menu):
        data = pr.forecast(dictModels, df)
        data = json.loads(data)
        return jsonify(data[menu])

api.add_resource(Predictive, '/api/predictive')
api.add_resource(PredictiveOne, '/api/predictive/<menu>')

if __name__ == '__main__':
    app.run(port=8000, debug=True)