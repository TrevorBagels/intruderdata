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
	
	@commands.command(brief='shows you your stats over time')
	async def mystats(self, ctx, stat):
		me = await self.bot.getme(ctx)
		if me == None: return
		