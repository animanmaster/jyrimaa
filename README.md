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
`jython -J-cp sqlitejdbc-v056.jar scoreState.py`

(Or put the sqlitejdbc-v056.jar in the Java classpath and just do `jython scoreState.py`)



