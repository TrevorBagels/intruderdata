from dev import data as D
from dev import utils
import pandas as pd
import time, random, requests, pymongo, threading
from matplotlib import pyplot
import numpy as np

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
			x_axis.append(xy["timestamp"])
			y_axis.append(xy["value"])
		s = pd.Series(y_axis, x_axis).drop_duplicates()
		timeline = s.resample(freq).ffill().interpolate()
		x = 4
		return timeline



values = [[], [], []]
xyz = []

m = Main()
for p in m.players.find({"stats": {"$exists": True}}):
	level_float = p['stats']['level'] + (p['stats']['levelXp'] / p['stats']['levelXpRequired'])
	#values[0].append(p['loginCount'])
	values[0].append(level_float)
	kdr = (p['stats']['kills']) / max(p['stats']['deaths'], 1)
	values[1].append(kdr)
	color = "#0313fc"
	if p['stats']['kills'] <= 0: color = "#fc9403"
	if p['stats']['deaths'] <= 0: color = "#fc03d2"
	if p['stats']['deaths'] <= 0 and p['stats']['kills'] <= 0: color = "#03fc0b"
	values[2].append(color)
	#values[1].append(utils.from_iso8601(p["firstLogin"]))
	#values[1].append(p['stats']['levelXpRequired'])

for a in range(len(values[0])):
	xyz.append((values[0][a], values[1][a], values[2][a]))
def sortingfunc(v):
	return v[0]
xyz.sort(key=sortingfunc)
values = [[],[],[]]
for v in xyz:
	values[0].append(v[0])
	values[1].append(v[1])
	values[2].append(v[2])



pyplot.scatter(values[0], values[1], s=2, c=values[2], alpha=.2)
pyplot.xlabel("level")
pyplot.ylabel("KDR")
pyplot.yscale("log")
m, b = np.polyfit(values[0], values[1], 1)
x = np.array(values[0])
pyplot.plot(x, m*x + b)
pyplot.show()
#pyplot.xscale("log")
