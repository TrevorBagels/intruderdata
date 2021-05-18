import colorama, sys, datetime
from colorama.ansi import Fore



class Logger:
	def __init__(self, verbosity=1, file=None, logs_db=None, utc=False, timestamp=True):
		colorama.init()
		self.verbosity = verbosity
		self.file = file
		self.db = None
		self.logs_db = logs_db
		self.utc = utc
		self.timestamp = timestamp


	def setup_database(self, db_name, collection="logs", client_address= "mongodb://localhost:27017/"):
		import pymongo
		client = pymongo.MongoClient(client_address)
		self.db = self.client[db_name]
		self.logs_db = self.db[collection]

	def _timestamp(self) -> str:
		dt = datetime.datetime.now()
		if self.utc: dt = dt.astimezone(datetime.timezone.utc)
		return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


	def log(self, *args, t="normal", v=2, end=None):
		"""Prints stuff. "normal", "good", "warn", "bad", "important
		"""
		colors = {"normal": Fore.BLUE,  "good":Fore.GREEN, "warn": Fore.YELLOW, "bad": Fore.RED, "important": Fore.MAGENTA}
		if t not in colors: t == "warn"
		
		p = f"{colors[t]}{colorama.Style.BRIGHT}"
		timestamp = self._timestamp()
		if self.verbosity >= v:
			print(timestamp, p, *args, colorama.Style.RESET_ALL)
		stringed_args = []
		for x in args:
			stringed_args.append(str(x))
		
		if self.logs_db != None:
			self.logs_db.insert_one({"time": timestamp, "message": " ".join(stringed_args), "verbosity": v, "type": t})
		