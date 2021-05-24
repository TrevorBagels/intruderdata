from dev import data as D
from dev import utils
import pandas as pd
import time, random, requests, pymongo, threading
from matplotlib import pyplot

class Main:
	def __init__(self):
		self.config = D.Config.from_dict(utils.load_json("./config.json"))
		self.client = pymongo.MongoClient(self.config.mongodb_client)
		self.setup_database()
		self.players = self.db["players"]
		self.rooms = self.db["rooms"]

	
	def setup_database(self):
		self.db = self.client[self.config.dbname]
		collections = ["rooms", "players", "maps", "discord"]
		for collection_name in collections:
			if collection_name not in self.db.list_collection_names():
				self.db.create_collection(collection_name)