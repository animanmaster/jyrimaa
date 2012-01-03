My little sandbox for researching Arimaa heuristics.

It's a mess right now, but if you want to play around with it, feel free to do so.

Visit www.arimaa.com to learn more about the game, play the game online, learn about current research in AI for the game, along with resources for building your own game-playing bot! :D

Requirements
------------
* You need a games database to be able to examine games. I've compiled an sqlite database with of all the games (as of November 2011) from the www.arimaa.com site with the data I thought was relevant to me. Here's a link to the sqlite database I'm using (and whose schema is included in this repo): http://www.mediafire.com/?53thq2wp9a2i60s
* Java 1.5+ 
* Jython 2.5.2 (other versions of Jython may work, but this is what I'm using)

Note that you _can_ use just plain Python, but I'm using Swing for the GUI stuff in visualize.py. If you don't need that, or want to use Tk or something, go right ahead.

Running
-------
Make sure the sqlite jar is in your Java classpath when you run the scripts. If you don't wanna copy it to a global lib directory, do this:

`jython -J-cp sqlitejdbc-v056.jar jyrimaa.py <game_id> <turn_id> [<path_to_db>]`

where game_id and turn_id correspond to a game_id and turn_id from the database. If a path to the games.db file isn't provided, the script will try to use ./games.db.

If you're in a bash shell, you can just do `./run jyrimaa.py <game_id> <turn_id> [<path_to_db>]` to save some typing.

E.g.: `./run jyrimaa.py 4 26b`


