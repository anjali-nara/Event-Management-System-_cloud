# from flask import Flask
# from flask_pymongo import PyMongo
# from flask_jwt_extended import JWTManager
# import os

# app = Flask(__name__)import os
# print(os.environ.get('PYTHONPATH', 'PYTHONPATH is not set'))

# app.config["MONGO_URI"] = ""


# app.secret_key = 'event'
# ca = certifi.where()

# mongo = PyMongo(app)


from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
import os
import certifi

app = Flask(__name__)
print(os.environ.get('PYTHONPATH', 'PYTHONPATH is not set'))

app.config["MONGO_URI"] = ""

app.secret_key = 'event'
ca = certifi.where()

mongo = PyMongo(app)
