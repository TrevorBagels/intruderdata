from datetime import datetime
from .prodict import Prodict
from . import utils


class Config(Prodict):
	mongodb_client:		str
	dbname:				str
	check_interval:		int
	speed_limit:		float
	player_scan_speed_limit:	float
	my_id:				int #steam ID

	def init(self):
		self.mongodb_client = "mongodb://localhost:27017/"
		self.dbname = "intruderdata"
		self.check_interval = 120
		self.speed_limit = .175
		self.player_scan_speed_limit = 7200 #4 hours
		self.my_id = 1234567891234


class Scores(Prodict):
	guards:		int
	intruders:	int

class User(Prodict):
	id:			int
	steamId:	str
	name:		str
	avatarUrl:	str
	role:		str
	loginCount:	int
	firstLogin:	datetime #timestamp
	lastLogin:	datetime #timestamp
	lastUpdate:	datetime #timestamp
	status:		any #probably string?




class Map(Prodict):
	id:			int
	author:		User
	name:		str
	gamemode:	str
	thumbnailUrl: 	str
	isMapMakerMap:	bool
	tags:			list[str]
	lastUpdate:		str #timestamp. doesn't have the Z, just has the date. so we'll leave this as a string rather than trying to convert it. plus, we aren't doing much with the maps anyways, and the collection for maps is tiny.

class Room(Prodict):
	id:			int
	name:		str
	motd:		str
	password:	str #md5 hash
	region:		str #US, EU, AU, etc
	official:	bool
	ranked:		bool
	style:		any #idk, always seems to be null
	version:	int
	position:	int
	scores:		list[Scores]
	currentMap:	Map
	maps:		list[Map]
	rules:		Prodict #this doesn't matter too much
	maxAgents:	int
	agentCount:	int
	specatatorSlots:	int
	joinableBy:			str #normally says "agent"
	blacklist:			list[str]#???
	creatorId:			int
	#tuning:				any

class Stats(Prodict):
	id:					int
	agentId:			int
	matchesWon:			int
	matchesLost:		int
	roundsLost:			int
	roundsTied:			int
	roundsWonElimination:	int
	roundsWonCapture:		int
	roundsWonHack:			int
	roundsWonTimer:			int
	roundsWonCustom:		int
	timePlayed:			int
	kills:				int
	teamKills:			int
	deaths:				int
	arrests:			int
	gotArrested:		int
	captures:			int
	pickups:			int
	networkHacks:		int
	survivals:			int
	suicides:			int
	knockdowns:			int
	gotKnockedDown:		int
	teamKnockdowns:		int
	teamDamage:			int

	level:				int
	levelXp:			int
	levelXpRequired:	int
	totalXp:			int

class Status(Prodict):
	id:			int
	agentId:	int
	roomId:		int
	lastUpdate:	datetime #timestamp
	online:		bool
	room:		any

class Votes(Prodict):
	id:				int
	agentId:		int
	attributeId:	int
	positive:		int
	negative:		int
	received:		int
	lastUpdate:		datetime



class Rooms(Prodict):
	totalCount:	int
	data:		list[Room]

class VersionedData(Prodict):
	timestamp:		datetime 
	value:			any
	def init(self):
		self.timestamp = utils.now()

	#when pushing to list
	#if the value of the last item in the list != this value, append twice.
	#if the value of the last item in the list == this value, change the timestamp of the last item in the list.
	#this lets us keep track of changes without having a huge list

class MongoStatsHistory(Prodict):
	level:			list[VersionedData]
	matchesWon:		list[VersionedData]
	matchesLost:	list[VersionedData]
	timePlayed:		list[VersionedData]
	kills:			list[VersionedData]
	teamKills:		list[VersionedData]
	deaths:			list[VersionedData]
	arrests:		list[VersionedData]
	gotArrested:	list[VersionedData]
	level:			list[VersionedData]
	survivals:		list[VersionedData]
	knockdowns:		list[VersionedData]
	networkHacks:	list[VersionedData]
	captures:		list[VersionedData]
	pickups:		list[VersionedData]
	suicides:		list[VersionedData]
	teamKnockdowns:	list[VersionedData]
	totalXp:		list[VersionedData]

class MongoUser(Prodict):
	_id:			int
	lastUpdated:	datetime #last time we updated this user with api calls
	steamId:		str
	name:			str
	avatarUrl:		str
	role:			str
	loginCount:		int
	firstLogin:		datetime
	lastLogin:		datetime
	lastUpdate:		datetime
	repPositive:	int
	repNegative:	int
	roleHistory:		list[VersionedData]
	lastLoginHistory:	list[VersionedData]
	nameHistory:		list[VersionedData]
	loginCountHistory:	list[VersionedData]
	avatarUrlHistory:	list[VersionedData]
	repPositiveHistory:	list[VersionedData]
	repNegativeHistory:	list[VersionedData]
	
	statsHistory:		MongoStatsHistory

	roomHistory:		list[VersionedData] #int for room ID. to check this, we also have to keep track of the current players in each room, so we know when one leaves.
	playTimeHistory:	list[VersionedData] #requires api calls to https://api.intruderfps.com/agents/{steamid}/stats to get this info. So it won't be updated super often, more like once a day.

	




class MongoRoom(Prodict):
	_id:					int
	name:					str
	motd:					str
	password:				str
	region:					str
	official:				bool
	ranked:					bool
	version:				int
	position:				int
	maxAgents:				int
	joinLog:				list[VersionedData]
	leaveLog:				list[VersionedData]
	currentPlayers:			list[int] #list of agent IDs
	agentCountHistory:		list[VersionedData] #int
	positionHistory:		list[VersionedData] #int
	versionHistory:			list[VersionedData] #int
	mapHistory:				list[VersionedData] #int (map ID)
	joinableBy:				str
	creatorId:				int
	timeFound:				datetime #first time this room was discovered
	#score_history:	list[Scores]



"""

"""
class MongoMatch(Prodict):
	#fire:		list[int] #steam IDs
	#water:		list[int] #steam IDs
	room:		int #room ID
	timestamp:	datetime#when we noticed this match
	joins:		list[VersionedData] #time log of when agents joined. most of them should have joined at timeStart. value=agent id
	leaves:		list[VersionedData] #time log of when agents left. value=agent id
	part1:		Scores #Fire vs Water
	part2:		Scores #Water vs Fire


