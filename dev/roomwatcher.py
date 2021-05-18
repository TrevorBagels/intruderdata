import threading, requests, datetime, time
from numpy import diff

import pandas as pd
from . import utils

class RoomWatcher:
	def __init__(self, m):
		from . import main
		self.main:main.Main = m
		self.watching = None #room ID
		self.watch_thread = None #thread
	

	def watch(self, room_id):
		if self.watch_thread != None:
			return
		self.main.log("Watching room", self.main.rooms.find_one({"_id": room_id})["name"], t="good", v=0)
		self.watching = room_id
		self.watch_thread = threading.Thread(target=self.watch_loop)
		self.watch_thread.start()
		

	
	def stop_watching(self):
		self.main.log("No longer watching room", t="good", v=0)
		self.watching = None
		self.watch_thread = None
	

	def watch_loop(self):
		while True:
			if self.watching == None:
				break
			#get the room
			agents = self.main.get_agents(self.watching)
			if agents == None:
				self.stop_watching()
				break
			for a in agents:
				self.main.scan_player(a, current_room=self.watching)
				self.main.scan_player_deep(a.id)
				time.sleep(.2)
				allchanges = self.get_stat_changes(a.id)
				changes = allchanges[0]
				if changes["teamKills"] != 0:
					self.main.log(a.name + " had", changes["teamKills"], f"team kills within the past {allchanges[1]['teamKills']} minutes.", v=0, t="important")
				if changes["kills"] > 4:
					self.main.log(a.name + " had", changes["kills"], f"kills within the past {allchanges[1]['kills']} minutes.", t="important", v=0)
				for c in ["repPositiveHistory", "repNegativeHistory"]:
					if changes[c] != 0:
						self.main.log(a.name + f" had {changes[c]}" + {"repPositiveHistory": "upvote(s)", "repNegativeHistory": "downvote(s)"}[c] + f" in the past {allchanges[1][c]} minutes. ")
				
			time.sleep(120) #sleep for two minutes

	
	def get_stat_changes(self, agent_id, look_for=["kills", "teamKills", "deaths", "repPositiveHistory", "repNegativeHistory"]):
		changes = {}
		changes_time_stretch = {}
		for x in look_for:
			changes[x] = 0
			changes_time_stretch[x] = 0 #0 minutes
		
		agenthistory = self.main.players.find_one({"_id": agent_id})
		for c in changes:
			if c not in ["repPositiveHistory", "repNegativeHistory"]:
				timeline = agenthistory["statsHistory"][c]
			else:
				timeline = agenthistory[c]
			
			#if type(timeline) == type(None): continue #skip this because something went wrong and i ain't gonna debug it right now.
			
			current = timeline[len(timeline)-1]
			
			difference = 0
			timedifference = 0
			if len(timeline) >= 4:
				difference = timeline[len(timeline)-1]["value"] - timeline[len(timeline)-1 - 2]["value"]
				timedifference = (timeline[len(timeline)-1]["timestamp"] - timeline[len(timeline)-1 - 2]["timestamp"]).total_seconds()/60
			
			if difference != 0 and timedifference <= 40:
				changes[c] = difference
				changes_time_stretch[c] = int(timedifference) #minutes
		return (changes, changes_time_stretch)


	def round_time_to_minute(self, ts:datetime.datetime, base=6):
		minute = utils.round_to_nearest(ts.minute, base)
		timestamp = datetime.datetime(year=ts.year, month=ts.month, day=ts.day, hour=ts.hour, minute=minute)
		return timestamp
		

	def get_timeline(self, data:list, freq=".1H"):
		x_axis = []
		y_axis = []
		for xy in data:
			x_axis.append(xy["timestamp"])
			y_axis.append(xy["value"])
		s = pd.Series(y_axis, x_axis).drop_duplicates()
		try:
			timeline = s.resample(freq).ffill().interpolate() #every 6 minutes
			return timeline
		except:
			return None

			


			

