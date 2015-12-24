from flask import Flask, abort
from flask_restful import Resource, Api, reqparse
import numpy as np
from data_manager import DataManager
import database_api

app = Flask(__name__)
api = Api(app)

data_manager = DataManager()

database_api.data_manager = data_manager

api.add_resource(database_api.DatabaseAPI, '/database')
api.add_resource(database_api.DatabaseElementAPI, '/database/<path:image_url>')

if __name__ == '__main__':
    app.run(debug=True)