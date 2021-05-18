# intruderdata
A data scraper for Intruder (a videogame).

Requirements:
  * MongoDB
  * Python 3.9
    * pymongo
    * scipy, matplotlib, numpy, pandas (for using the analysis scripts, which are a work in progress)


To use, make sure that you're hosting a mongoDB server somewhere (such as your own machine) and create a database called "intruderdata" (can be changed in config.json.)
Then, simply run `python3 -m dev`

If you play the game, and want to monitor yourself, change the `"my_id"` value in the config to your steam ID. This will cause the program to monitor any rooms that you might be currently playing in, and it'll update statistics on each player in that room more frequently.


## What's this for?

I enjoy playing Intruder, but I also like data. And once I figured out that there was an open API for intruder, I decided to make something to track my stats over time. And, in doing so, I made it track everyones stats over time, keeping track of their history, which eventually, I hope to use as sample datasets when going through data science courses. 

Additionally, I'm planning on implementing a feature that can analyze the match you're currently playing in, and tell you things like your likelihood of winning, what strategies to expect from the other team, etc, by using the current stats of all players and the history of their stats (how successful they are at different times of the day / week).

And sometimes, I have random questions, like "do people perform significantly better at this videogame during the weekend rather than the week?"
And the database that this program puts together can provide a means to answering such questions.
