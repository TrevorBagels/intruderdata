import os, time, random, sys, discord, datetime
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import get
from ... import utils
from ..bot import AssistantBot
from ...prodict import Prodict

from ..modules import rooms as therooms


class Module(commands.Cog):
	def __init__(self, bot):
		self.bot:AssistantBot = bot
		self.main = self.bot.main
		self.roomsmodule = therooms.Rooms(self.main)
	
	@commands.command(brief='shows you who\'s playing in the rooms you usually play.')
	async def whosonline(self, ctx):
		me = await self.bot.getme(ctx)
		if me == None: return
		rooms = self.roomsmodule.what_rooms({"_id": me.playerId})
		for room in rooms:
			name = room['name']
			if "<color=yellow>" in name:
				name = name.replace("<color=yellow>", "").replace("</color>", "")

			embed = discord.Embed(title=name, desc=f"{len(room['players'])} player(s)")
			for pname in room['players']:
				embed.add_field(name="\u200E", value=pname, inline=True)
			await ctx.send(embed=embed)

		


	



	
	
