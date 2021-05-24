from .base import BaseModule
class Briefcase(BaseModule):
	def __init__(self, main):
		super().__init__(main)

	def hack_or_case(self, room_id):
		room = self.rooms.find_one({"_id": room_id})
		players = room["currentAgents"]
		likleyhood = []
		for x in players:
			p = self.players.find_one({"_id": x})
			captures = self.normalize(p['stats']['captures'], p['stats']['level'])
			hacks =    self.normalize(p['stats']['networkHacks'], p['stats']['level'])
			capturesRelative = captures - self.avgs['captures']["mode"]
			hacksRelative = hacks - self.avgs['networkHacks']['mode']
			likleyhood.append(hacksRelative > capturesRelative)
			#likleyhood.append( (x, hacksRelative, capturesRelative ) )
		
		if likleyhood.count(True) > likleyhood.count(False):
			return "hack computers"
		else:
			return "take the briefcase"
			#hacksgood = self.above_average(self.normalize(hacks, p['stats']['level']), self.avgs["networkHacks"]["max"], self.avgs["networkHacks"]["mode"], d=3)
		def sorting(value):
			return value[1]
		likleyhood.sort(key=sorting, reverse=True)
		return likleyhood

	def who_has_briefcase(self, room_id):
		room = self.rooms.find_one({"_id": room_id})
		players = room["currentAgents"]
		likleyhood = []
		for x in players:
			p = self.players.find_one({"_id": x})
			captureRate = int(p['stats']['captures'] / max(p['stats']['pickups'], 1)*1000)/10
			likleyhood.append( (x, captureRate) )
		def sorting(value):
			return value[1]
		likleyhood.sort(key=sorting, reverse=True)
		return likleyhood
		#player = self.players.find_one({"_id": likleyhood[0][0]})
		#print(player['name'], f"(level {player['stats']['level']})", f"most likely has the briefcase. They've picked up the briefcase {player['stats']['pickups']} times with a capture success rate of {likleyhood[0][1]}%.")