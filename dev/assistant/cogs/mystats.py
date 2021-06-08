import os, time, random, sys, discord, datetime
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import get
from ... import utils
from ..bot import AssistantBot
from ...prodict import Prodict

from ..modules import statsimg


class Module(commands.Cog):
	def __init__(self, bot):
		self.bot:AssistantBot = bot
		self.main = self.bot.main
		self.figuremodule = statsimg.Module(self.main)
	
	@commands.command(brief='shows you your stats over time')
	async def mystats(self, ctx, stats):
		me = await self.bot.getme(ctx)
		if me == None: return
		stats = stats.split(",")
		chosen_options = []
		options = ["level", "matchesWon", "matchesLost", "timePlayed", "kills", "teamKills", "deaths", "arrests", "gotArrested", "survivals", "knockdowns", "networkHacks", "captures", "pickups", "suicides", "teamKnockdowns", "totalXp"]
		for stat in stats:
			option = None
			for i, o in enumerate(options):
				if o.lower() == stat.lower():
					option = o
			if option == None:
				await ctx.channel.send("Invallid stat. Please select from the following: ``" + ", ".join(options) + "``")
				return
			if option != None:
				chosen_options.append(option)
		
		path = self.figuremodule.display_timeline(me.playerId, chosen_options)
		with open(path, 'rb') as f:
			picture = discord.File(f)
			await ctx.channel.send(file=picture)
		