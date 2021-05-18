from datetime import datetime, timezone
from dev import data as D
from dev import utils
import pandas as pd
import numpy as np
from scipy import stats
import time, random, requests, pymongo, threading
from matplotlib import pyplot

class Main:
	def __init__(self):
		self.config = D.Config.from_dict(utils.load_json("./config.json"))
		self.client = pymongo.MongoClient(self.config.mongodb_client)
		self.setup_database()
		self.players = self.db["players"]
		self.rooms = self.db["rooms"]
		self.dataTargets = ["level", "matchesWon", "matchesLost", "kills", "teamKills", "arrests", "deaths"]
	

	def setup_database(self):
		self.db = self.client[self.config.dbname]
		collections = ["rooms", "players", "maps"]
		for collection_name in collections:
			if collection_name not in self.db.list_collection_names():
				self.db.create_collection(collection_name)
	
	def normalize(self, stat, level):
		#return stat/(level)
		return stat / max(level, 1)
		#return stat

	def getstats(self):
		dataTargets = self.dataTargets
		data = {}
		for x in dataTargets:
			data[x] = []
		for p in self.players.find():
			if "stats" in p and p["stats"] != None:
				if p['stats']['level'] < 10: continue
				for target in dataTargets:
					data[target].append(self.normalize(p["stats"][target], p["stats"]["level"]))
		print("Raw data collected.")
		#now we have some raw data. Do something with it
		dataStats = {}
		for x in dataTargets:
			dataStats[x] = {"range":0, "mean":0, "median":0, "mode":0}
			dataStats[x]["max"] = float(np.max(data[x]))
			dataStats[x]["min"] = float(np.min(data[x]))
			dataStats[x]["range"] = float(dataStats[x]["max"] - dataStats[x]["min"])
			dataStats[x]["mean"] = np.average(data[x])
			dataStats[x]["median"] = np.median(data[x])
			dataStats[x]["mode"] = np.average(data[x])
			#dataStats[x]["mode"] = stats.mode(data[x])
		for k, v in dataStats.items(): print(k + ":", v)
		utils.save_json("datastats.json", dataStats)

	def analyze(self, key):
		self.dataStats = utils.load_json("datastats.json")
		player = self.players.find_one(key)
		target_data = player["stats"]
		#print(player["name"])
		for target, stats in self.dataStats.items():
			value = self.normalize(target_data[target], target_data["level"])
			if self.above_average(value, stats["max"], stats["mode"], d=2):
				print(player['name'], ' --- ', target, "is above average. ", target_data[target], "| normalized:", value, "| average:", stats["mode"])
			#if self.below_average(value, stats["min"], stats["mode"]):
			#	print(target, "is below average. ", target_data[target], "| normalized:", value)


	def above_average(self, value, maxi, avg,d=2):
		return value > (avg + (maxi - avg)/d)
	def below_average(self, value, mini, avg,d=2):
		return value < (avg - (avg - mini)/d)
		
	def when_played(self, key):
		player = self.players.find_one(key)
		log = []
		for room in self.rooms.find({"joinLog": {"$exists": True}, "leaveLog": {"$exists": True}}):
			for x in room["joinLog"]:
				if x['value'] == player["_id"]: log.append( ( utils.local(x["timestamp"]), "join", room["_id"] ) )
			for x in room["leaveLog"]:
				if x['value'] == player["_id"]: log.append( ( utils.local(x["timestamp"]), "leave", room["_id"] ) )
		def sort_log(value):
			return (utils.long_ago() - value[0]).total_seconds()
		log.sort(key=sort_log)
		
		for x in log:
			print(x[0], "\t", x[1], "\t", self.rooms.find_one({"_id": x[2]})["name"])
		
	def who_has_briefcase(self, roomId):
		room = self.rooms.find_one({"_id": roomId})
		players = room["currentAgents"]
		likleyhood = []
		for x in players:
			p = self.players.find_one({"_id": x})
			captureRate = int(p['stats']['captures'] / max(p['stats']['pickups'], 1)*1000)/10
			likleyhood.append( (x, captureRate) )
		def sorting(value):
			return value[1]
		likleyhood.sort(key=sorting, reverse=True)
		player = self.players.find_one({"_id": likleyhood[0][0]})
		
		print(player['name'], f"(level {player['stats']['level']})", f"most likely has the briefcase. They've picked up the briefcase {player['stats']['pickups']} times with a capture success rate of {likleyhood[0][1]}%.")

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

for p in m.players.find():
	key = {"_id":  p["_id"]}
	for x in ["role", "lastLogin", "name", "loginCount", "avatarUrl"]:
		m.players.update_one(key, {"$set": {(x + "History"): [D.VersionedData(value=p[x]), D.VersionedData(value=p[x])]}})


m.when_played({"name": "bagel", "stats.level": 69})
m.who_has_briefcase(76555)
#m.getstats()

#for x in m.players.find({"stats.level": {"$lt": 5}, "firstLogin": {"$gt": "2021-04-15"}}):
#	m.analyze({"_id": x["_id"]})