import os, time, random, sys, discord, datetime
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import get
from ... import utils
from ..bot import AssistantBot
from ...prodict import Prodict




class Module(commands.Cog):
	def __init__(self, bot):
		self.bot:AssistantBot = bot
		self.main = self.bot.main
		from ..modules import briefcase
		self.bc = briefcase.Briefcase(self.main)
		self.commands = {
			"case": self.briefcase,
			"strategy": self.hack_or_case
		}
		
	async def briefcase(self, ctx, me):
		myroom = self.bc.current_room(me["playerId"])
		if myroom == None:
			await ctx.channel.send("Could not find your room!")
		else:
			options = self.bc.who_has_briefcase(myroom)
			embed = discord.Embed(title="People that might have briefcase")
			for x in options[:5]:
				p = self.main.players.find_one({"_id": x[0]})
				desc = f"Has grabbed briefcase {p['stats']['pickups']} time(s).\nCapture rate: {x[1]}%\n Level: {p['stats']['level']}\nKDR: {round(p['stats']['kills']/p['stats']['deaths'], 2)}"
				embed.add_field(name=p["name"], value=desc, inline=True)
			await ctx.send(embed=embed)
	
	async def hack_or_case(self, ctx, me):
		myroom = self.bc.current_room(me["playerId"])
		if myroom == None:
			await ctx.channel.send("Could not find your room!")
		else:
			horc = self.bc.hack_or_case(myroom)
			await ctx.channel.send(f"People are more likely to **{horc}** in this room.")

	@commands.command(brief='shows you your stats over time')
	async def advice(self, ctx, *args):
		request = " ".join(args)
		me = await self.bot.getme(ctx)
		if me == None: return
		for x in self.commands:
			if x in str(request):
				await self.commands[x](ctx, me)

		