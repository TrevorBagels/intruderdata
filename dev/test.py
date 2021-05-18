import requests, json
import hashlib
import crypt




a = requests.get("https://api.intruderfps.com/rooms?perPage=100")
data = a.json()
rooms = data["data"]
pwdhashed = ""
pwdplain = "thepasswordtothisroomispassword"
thing = None
for x in rooms:
	if x["password"] != None:
		#print(x["id"], ":", x["name"], ":", x["password"])
		#print(x)
		if x["name"] == pwdplain:
			pwdhashed = x["password"]
			thing = x
print(pwdhashed)
salts = [thing["id"], thing["name"], thing["creator"]["steamId"], thing["creator"]["id"], thing["creator"]["name"]]
for salt in salts:
	salt = str(salt)
	hashed = hashlib.md5((salt + "." + pwdplain).encode()).hexdigest()
	print(hashed)
	if hashed == pwdhashed:
		print("SALT:", x)

