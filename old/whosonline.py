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
	
	def what_rooms(self, key):
		player = self.players.find_one(key)
		rooms = []
		room_freq = {}
		for room in self.rooms.find({"joinLog": {"$exists": True}, "leaveLog": {"$exists": True}}):
			room_freq[room["_id"]] = 0
			for x in room["joinLog"] + room["leaveLog"]:
				if x['value'] == player['_id']:	
					room_freq[room["_id"]] += 1
					if room["_id"] not in rooms: rooms.append(room["_id"])
		def sort_rooms(value):
			return room_freq[value]
		rooms.sort(key=sort_rooms, reverse=True)
		
		for x in rooms[:4]:
			room = self.rooms.find_one({"_id": x})
			names = []
			for player_id in room["currentAgents"]:
				try:
					p = self.players.find_one({"_id": player_id})
					names.append(f"({p['stats']['level']})  " + p["name"])
				except:
					names.append(f"[unknown][{player_id}]")
			print(f"{len(names)} player(s) currently playing in", room["name"])
			self.prettyprint2collumns(names)
			print("\n")
			
	def prettyprint2collumns(self, names):
		c1 = []
		c2 = []
		for i, x in enumerate(names):
			if i % 2:
				c1.append(x)
			else:
				c2.append(x)
		c1size = 50
		for x in c1:
			if len(x) > c1size: c1size = len(x)
		c1size += 10
		for i in range(len(c1)):
			txt = c1[i] + ((c1size - len(c1[i])) * " ")
			if len(c2)-1 >= i:
				txt += c2[i]
			print(txt)


	
	def setup_database(self):
		self.db = self.client[self.config.dbname]
		collections = ["rooms", "players", "maps"]
		for collection_name in collections:
			if collection_name not in self.db.list_collection_names():
				self.db.create_collection(collection_name)



m = Main()


m.what_rooms({"steamId": str(m.config.my_id)})