from pymongo.database import Database
from . import data as D
from . import utils
import time, random, requests, pymongo, threading
from .roomwatcher import RoomWatcher
from . import logger
class Main:
	def __init__(self):
		self.config = D.Config.from_dict(utils.load_json("./config.json"))
		utils.save_json("./config.json", self.config.to_dict())
		self.client = pymongo.MongoClient(self.config.mongodb_client)
		self.setup_database()
		self.players = self.db["players"]
		self.rooms = self.db["rooms"]
		self.maps = self.db['maps']
		self.matches = self.db['matches']
		self.player_scan_queue = []
		self.logger = logger.Logger(logs_db=self.db["logs"])
		self.log = self.logger.log
		self.watcher = RoomWatcher(self)
		self.running = True
		threading.Thread(target=self.player_scan_thread).start()
		while self.running:
			start = time.time()
			self.log("Scanning rooms.", v=1)
			self.main_loop()
			elapsed = time.time() - start
			self.log(f"Done! Took {utils.time_elapsed(elapsed)}", v=1, t="good")
			time.sleep(max(self.config.check_interval - elapsed, 0.1))
	
	def get(self, url):
		headers = {"User Agent": "Hello there!"}
		try:
			req = requests.get(url, headers=headers)
			if req.ok:
				try:
					data = req.json()
					self.log("Request to", url, "| Content:", req.content.decode())
					return data
				except:
					self.log("Could not decode JSON!", "URL:", url, " | Content:", req.content.decode(), v=0, t="bad")
					return None
			else:
				self.log("Request not ok!", "URL:",url, "| Content:", req.content.decode(), t="bad", v=0)
				return None
		except Exception as e:
			self.log("Request failed!", "URL:", url, "Error: ", str(e), v=0, t="bad")
			return None
			
		

			



	
	def setup_database(self):
		self.db = self.client[self.config.dbname]
		collections = ["rooms", "players", "maps", 'matches', "logs"]
		for collection_name in collections:
			if collection_name not in self.db.list_collection_names():
				self.db.create_collection(collection_name)
	

	def player_scan_thread(self):
		while self.running:
			for x in self.player_scan_queue.copy():
				self.scan_player_deep(x)
				self.players.update_one({"_id": x}, {"$set": {
					"lastUpdated": utils.to_iso8601(utils.now())
				}})
				self.player_scan_queue.remove(x)
			time.sleep(3)
				

	def scan_player_deep(self, player_id):
		time.sleep(.7)
		self.log("Scan player", player_id, v=2)
		steamid = self.players.find_one({"_id": player_id})["steamId"]
		
		stats = D.Stats.from_dict(self.get(f"https://api.intruderfps.com/agents/{steamid}/stats"))
		
		self.players.update({"_id": player_id}, {"$set": {"stats": stats}})
		self.set_if_not_found(self.players, player_id, "statsHistory", D.MongoStatsHistory())
		
		votes = D.Votes.from_dict(self.get(f"https://api.intruderfps.com/agents/{steamid}/votes")[0])

		def update_history(key, value):
			currentHistory = []
			if key in self.players.find_one({"_id": player_id})["statsHistory"] and self.players.find_one({"_id": player_id})["statsHistory"][key] != None:
				currentHistory = self.players.find_one({"_id": player_id})["statsHistory"][key]
			new_versions = self.version_update(currentHistory, value)
			self.players.update({"_id": player_id}, {"$set": {f"statsHistory.{key}": new_versions}})
		
		for x in self.players.find_one({"_id": player_id})["statsHistory"]:
			update_history(x, stats[x])
		self.players.update({"_id": player_id}, {"$set": {"repPositive": votes.positive, "repNegative": votes.negative}})
		self.update_history(self.players, player_id, "repPositiveHistory", votes.positive)
		self.update_history(self.players, player_id, "repNegativeHistory", votes.negative)




	def main_loop(self):
		rooms = self.get_rooms()
		#add rooms and their data
		for x in rooms.data:
			self.scan_room(x)
			time.sleep(.1 + self.config.speed_limit)


	def remove_null_from_dict(self, d:dict):
		newd = {}
		for k, v in d.items():
			if v != None:
				newd[k] = v
		return newd
	
	def set_if_not_found(self, collection, id, key, value):
		if key not in collection.find_one({"_id": id}):
			collection.update_one({"_id": id}, 
				{'$set': {key: value} }
				, upsert=True)


	def scan_room(self, room:D.Room):
		self.log("Scanning room", room.name, v=2)
		key = {"_id": room.id}
		roomData = D.MongoRoom()
		roomData._id = room.id

		for x in roomData.keys():
			if x in room.keys():
				roomData[x] = room[x]
		self.rooms.update(key, 
			{'$set': self.remove_null_from_dict(roomData) }, 
			upsert=True)
		
		if "timeFound" not in self.rooms.find_one(key):
			self.rooms.update_one(key, 
				{'$set': {"timeFound": utils.to_iso8601(utils.now())} }
				, upsert=True)
		#keys, and the keys of their values
		for x in [("agentCountHistory", "agentCount"), ("positionHistory", "position"), ("versionHistory", "version")]:
			self.update_history(self.rooms, roomData._id, x[0], room[x[1]])
		self.update_history(self.rooms, roomData._id, "mapHistory", room["currentMap"]["id"])
		for x in ["joinLog", "leaveLog"]: self.add_if_null(self.rooms, roomData._id, x, [])
		self.scan_map(room.currentMap)
		for x in room.maps:
			self.scan_map(x)
		
		me_found = False
		prev_agents = []
		if "currentAgents" in self.rooms.find_one({"_id": room.id}):
			prev_agents = self.rooms.find_one({"_id": room.id})["currentAgents"]
		
		if room.agentCount > 0:
			agents = self.get_agents(room.id)
			agent_ids = []
			for x in agents:
				agent_ids.append(x.id)
				self.scan_player(x, current_room=room.id)
				if int(x.steamId) == int(self.config.my_id):
					me_found = True
					if self.watcher.watching == None:
						self.watcher.watch(room.id)
			self.rooms.update_one(key, {"$set": {"currentAgents": agent_ids}})
		else:
			self.rooms.update_one(key, {"$set": {"currentAgents": []}})
		
		current_agents = self.rooms.find_one(key)["currentAgents"]
		agents_left = []
		agents_joined = []
		#find new agents, find ones that left, find ones that stayed
		for l in prev_agents:
			if l not in current_agents:
				agents_left.append(D.VersionedData(value=l))
		
		for j in current_agents:
			if j not in prev_agents:
				agents_joined.append(D.VersionedData(value=j))
		
		for x in agents_left:
			self.rooms.update_one(key, {"$push": {"leaveLog": x.to_dict()}})
			self.log(x['value'], "disconnected from", room.id)
		for x in agents_joined:
			self.rooms.update_one(key, {"$push": {"joinLog": x.to_dict()}})
			self.log(x['value'], "joined", room.id)

		#i am no longer in this room, stop watching it!				
		if me_found == False and self.watcher.watching == room.id:
			self.watcher.stop_watching()
					
				

	
	def scan_player(self, player:D.User, current_room=None):
		self.log("Quick scan of ", player.name, v=3)
		key = {"_id": player.id}
		userData = D.MongoUser()
		userData._id = player.id
		for x in userData.keys():
			if x in player.keys():
				userData[x] = player[x]
		self.players.update(key, 
		{"$set": self.remove_null_from_dict(userData) },
		upsert=True
		)

		self.set_if_not_found(self.players, player.id, "timeFound", utils.to_iso8601(utils.now()))

		for x in ["role", "lastLogin", "name", "loginCount", "avatarUrl"]:
			self.update_history(self.players, player.id, (x + "History"), self.players.find_one(key)[x])
		
		self.update_history(self.players, player.id, "roomHistory", current_room) #update room history

		#check last time api calls were made on this player. we might need to add them to the queue.
		self.set_if_not_found(self.players, player.id, "lastUpdated", utils.to_iso8601(utils.long_ago()))
		if (utils.now() - utils.from_iso8601(self.players.find_one(key)['lastUpdated'])).total_seconds() >= self.config.player_scan_speed_limit:
			if player.id not in self.player_scan_queue: self.player_scan_queue.append(player.id)
		
		
	def scan_map(self, m:D.Map):
		m = m.to_dict()
		self.maps.update({"_id": m['id']}, {"$set": 
			m
		}, upsert=True)

	
	
	def version_update(self, version_list:list, value):
		if len(version_list) == 0 or version_list[len(version_list)-1]['value'] != value:
			for x in range(2): version_list.append(D.VersionedData(value=value).to_dict()) #append twice
		elif version_list[len(version_list)-1]['value'] == value:
			version_list[len(version_list)-1]['timestamp'] = utils.to_iso8601(utils.now())
		return version_list

	def add_if_null(self, collection, id, key:str, value):
		if key not in collection.find_one({"_id": id}) or collection.find_one({"_id": id})[key] == None:
			collection.update_one({"_id": id}, {"$set": {key: value} })
	def update_history(self, collection, id:int, key:str, value):
		"""Updates a version history of an item in the database

		Args:
			collection: Collection to modify
			id (int): _id of the item in the collection
			key (str): key of the history list to modify
			value (any): the value at this time.
		"""
		if key not in collection.find_one({"_id": id}) or collection.find_one({"_id": id})[key] == None:
			collection.update_one({"_id": id}, {"$set": {key: []} })
		new_versions = self.version_update(collection.find_one({"_id": id})[key], value)
		collection.update({"_id": id}, {"$set": {key: new_versions}})


			


		

		

	
	def get_agents(self, room_id) -> list[D.User]:
		agents = self.get(f"https://api.intruderfps.com/rooms/{room_id}/agents")
		if agents == None: return None
		time.sleep(self.config.speed_limit)
		data = []
		for x in agents:
			data.append(D.User.from_dict(x))
		return data

	def get_rooms(self) -> D.Rooms:
		return D.Rooms.from_dict(self.get("https://api.intruderfps.com/rooms?perPage=100"))
	
	