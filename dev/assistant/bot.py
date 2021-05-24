import os, time, random, sys, discord, datetime, math
from discord.ext import tasks, commands
from discord.ext.commands.core import command
from discord.utils import get
import importlib

from ..prodict import Prodict
from .. import utils

class MongoDiscordUser(Prodict):
	_id:			int
	name:			str
	playerId:		int
	steamId:		int
	lastScanned:	datetime.datetime
	timeAdded:		datetime.datetime
	favoriteRooms:	list[int]
	permissions:	list[int]
	def init(self):
		self.lastScanned = utils.now()
		self.timeAdded = utils.now()	
		self.permissions = [0]

"""
Discord user schema
_id:			discord ID (int)
playerId:		player ID (int)
steamId:		steam ID (int)
lastScanned:	datetime, last time we did an analysis on this player
timeAdded:		datetime, when we added the player to the collection
favoriteRooms:	list[int], what rooms this player likes to play on
"""


class AssistantBot(commands.Bot):
	def __init__(self):
		from .main import Main
		self.main = Main()
		commands.Bot.__init__(self, command_prefix=",")
		from .cogs import whosonline, addme, advice
		self.WhosOnline = self.add_cog(whosonline.Module(self))
		self.AddMe = self.add_cog(addme.Module(self))
		self.Advice = self.add_cog(advice.Module(self))

	async def getme(self, ctx):
		me = self.main.db['discord'].find_one({"_id": ctx.author.id})
		if me == None:
			await ctx.channel.send("You need to add yourself to the database! Use `,addme [your name or Steam ID]` to add yourself.")
		else:
			me = MongoDiscordUser.from_dict(me)
		return me
