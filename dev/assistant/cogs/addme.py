import os, time, random, sys, discord, datetime
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import get
from ... import utils
from ..bot import AssistantBot, MongoDiscordUser




class Module(commands.Cog):
	def __init__(self, bot):
		self.bot:AssistantBot = bot
		self.main = self.bot.main
	
	@commands.command(brief="adds you to the database, allowing for easy use of commands. Please provide your name or steamId")
	async def addme(self, ctx, name_or_id):
		name_or_id = utils.try_convert(name_or_id, converter=int)
		if type(name_or_id) == str:
			#look them up
			options = []
			for p in self.main.players.find({"name": name_or_id}):
				try:
					options.append((p["stats"]["level"], p["name"], p["steamId"], p["_id"]))
				except:
					options.append(("?", p["name"], p["steamId"], p["_id"]))
			if len(options) == 0:
				await ctx.channel.send("No options found!")
			elif len(options) == 1:
				user = MongoDiscordUser(_id=ctx.author.id, playerId=options[0][3], steamId=options[0][2], name=options[0][1])
				self.main.db["discord"].update_one({"_id": ctx.author.id}, {"$set": user}, upsert=True)
				await ctx.channel.send("Added you to the database. ")
			else:
				embed=discord.Embed(title=f"players with name \"{name_or_id}\"")
				for o in options:
					embed.add_field(name=f"({o[0]}) {o[1]}", value=f"`{o[2]}`")
				embed.set_footer(text="Copy the steam ID and run `addme [steamId]`")
				await ctx.channel.send(embed=embed)
		else:
			player = self.main.players.find_one({"steamId": str(name_or_id)})
			if player == None:
				await ctx.channel.send("Could not find you!")
			else:
				user = MongoDiscordUser(_id=ctx.author.id, playerId=player["_id"], steamId=player["steamId"], name=player["name"])
				self.main.db["discord"].update_one({"_id": ctx.author.id}, {"$set": user}, upsert=True)
				await ctx.channel.send("Added you to the database. ")


	



	
	
