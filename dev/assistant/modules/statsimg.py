from .base import BaseModule
from matplotlib import pyplot
import pandas as pd

class Module(BaseModule):
	def __init__(self, main):
		super().__init__(main)
	

	def stats_img(self, playerId, stat_name, freq="last week") -> str: #returns path of image 
		"""returns path of image for player stats graph

		Args:
			stat_name ([type]): matchesWon, matchesLost, timePlayed, kills, teamKills, deaths, arrests, gotArrested, survivals, knockdowns, networkHacks, captures, pickups, suicides, teamKnockdowns, totalXp
			freq (str, optional): Defaults to "last week". Can be: last week, last month, today, all time, last year, last hour

		Returns:
			str: path of image
		"""
		return self.display_timeline(playerId, stat_name)
	


	def display_timeline(self, _id, keys, freq="1D"):
		k = {"_id": int(_id)}
		dfdata = {}
		for key in keys:
			data = self.players.find_one(k)['statsHistory'][key]
			timeline = self.get_timeline(data, freq=freq)
			#print(timeline)
			#timeline.plot()
			dfdata[key] = timeline.values
			dfdata["dates"] = timeline.axes[0]
		
		df = pd.DataFrame(dfdata)
		df.plot.line("dates")
		
		pyplot.savefig(f"./playerfigures/{_id}latest.png")
		return f"./playerfigures/{_id}latest.png"

	def get_timeline(self, data:list, freq=".1H"):
		x_axis = []
		y_axis = []
		for xy in data:
			x_axis.append(xy["timestamp"])
			y_axis.append(xy["value"])
		s = pd.Series(y_axis, x_axis).drop_duplicates()
		timeline = s.resample(freq).ffill().interpolate()
		return timeline
