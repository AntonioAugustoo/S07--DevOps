import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://devops_user:devops_password@mongodb:27017/")
MONGO_DB = os.getenv("MONGO_DB", "pokemon_trades")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
colecao_propostas = db.get_collection("propostas")
