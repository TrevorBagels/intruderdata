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
		collections = ["rooms", "players", "maps"]
		for collection_name in collections:
			if collection_name not in self.db.list_collection_names():
				self.db.create_collection(collection_name)
	
	def analyze(self, room):
		agents = None
		pass


	def get_timeline(self, data:list, freq=".1H"):
		x_axis = []
		y_axis = []
		for xy in data:
			x_axis.append(utils.from_iso8601(xy["timestamp"]))
			y_axis.append(xy["value"])
		s = pd.Series(y_axis, x_axis).drop_duplicates()
		timeline = s.resample(freq).ffill().interpolate() #every 6 minutes
		return timeline



m = Main()

m.display_timeline("rooms", 78105, "agentCountHistory")
time.sleep(3)