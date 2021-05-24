from ... import utils
class BaseModule:
	def __init__(self, main):
		self.main = main
		self.rooms = self.main.rooms
		self.players = self.main.players
		self.avgs = utils.load_json("datastats.json")
	
	def normalize(self, stat, level):
		#return stat/(level)
		return stat / max(level, 1)
		#return stat
	def above_average(self, value, maxi, avg,d=2):
		return value > (avg + (maxi - avg)/d)
	def below_average(self, value, mini, avg,d=2):
		return value < (avg - (avg - mini)/d)
	
	def current_room(self, player_id) -> int:
		for room in self.rooms.find({"joinLog": {"$exists": True}, "currentAgents": {"$exists": True}, "$where": "this.currentAgents.length > 0"}):
			if player_id in room["currentAgents"]:
				return room["_id"]
