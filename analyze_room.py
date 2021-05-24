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
	def display_timeline(self, coll, _id, key):
		room = self.db[coll].find_one({"_id": _id})
		print(room['name'])
		data = room[key]
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
			x_axis.append(xy["timestamp"])
			y_axis.append(xy["value"])
		s = pd.Series(y_axis, x_axis).drop_duplicates()
		timeline = s.resample(freq).ffill().interpolate() #every 6 minutes
		return timeline



m = Main()

#m.display_timeline("rooms", 76555, "agentCountHistory")

data = [[], []]
stuff = m.rooms.find_one({"_id": 76555})["agentCountHistory"]
for i in range(int(len(stuff)/2)):
	x = stuff[i*2]
	data[0].append(x["timestamp"])
	data[1].append(x["value"])

	
pyplot.plot(data[0], data[1])
pyplot.show()
#pyplot.xscale("log")


time.sleep(3)