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
