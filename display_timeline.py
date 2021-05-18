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
	
	def display_timeline(self, coll, _id, key, stats=False):
		if stats == False: data = self.db[coll].find_one({"_id": _id})[key]
		else: data = self.db[coll].find_one({"_id": _id})['statsHistory'][key]
		timeline = self.get_timeline(data, freq=".5H")
		#print(timeline)
		#timeline.plot()
		df = pd.DataFrame({"values": timeline.values, "dates": timeline.axes[0]})
		df.plot.line("dates", "values")
		pyplot.show()
		return df

	def get_timeline(self, data:list, freq=".1H"):
		x_axis = []
		y_axis = []
		for xy in data:
			x_axis.append(utils.from_iso8601(xy["timestamp"]))
			y_axis.append(xy["value"])
		s = pd.Series(y_axis, x_axis).drop_duplicates()
		timeline = s.resample(freq).ffill().interpolate()
		x = 4
		return timeline



m = Main()

m.display_timeline("players", 73140, "repPositiveHistory")
m.display_timeline("players", 73140, "repNegativeHistory")
m.display_timeline("players", 73140, "kills", stats=True)
time.sleep(3)