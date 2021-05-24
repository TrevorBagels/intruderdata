#start storing dates as ISO dates
import datetime, pymongo, json
from dev import main, utils
from dev import data as D


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



m = Main()
def fix_players(m):
	for p in m.players.find():
		print(p["_id"])
		for k in ["firstLogin", "lastLogin", "lastUpdate", "timeFound", "lastUpdated"]:
			if k in p:
				p[k] = utils.from_iso8601(p[k])
		if "stats" in p:
			p["stats"]['lastUpdate'] = utils.from_iso8601(p[k])
		for hlist in ["roleHistory", "lastLoginHistory", "nameHistory", "roomHistory", "repPositiveHistory", "repNegativeHistory", "avatarUrlHistory"]:
			if hlist in p:
				for x in p[hlist]:
					x["timestamp"] = utils.from_iso8601(x["timestamp"])
		if "statsHistory" in p:
			for hlist in p["statsHistory"]:
				for x in p["statsHistory"][hlist]:
					x["timestamp"] = utils.from_iso8601(x["timestamp"])
		m.players.update_one({"_id": p["_id"]}, {"$set":p})

def fix_rooms(m:Main):
	for r in m.rooms.find():
		r["timeFound"] = utils.from_iso8601(r['timeFound'])
		for hlist in ["agentCountHistory", "mapHistory", "positionHistory", "versionHistory", "joinLog", "leaveLog"]:
			if hlist in r:
				for x in r[hlist]:
					x["timestamp"] = utils.from_iso8601(x["timestamp"])
		m.rooms.update_one({"_id": r["_id"]}, {"$set":r})

	
fix_players(m)
fix_rooms(m)