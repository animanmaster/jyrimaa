from scoreState import *
from sys import argv
import time #I just imported time, itself! :O

__author__="Malik Ahmed"
__date__ ="$Dec 26, 2011 1:41:57 AM$"

def usage():
    print "usage:", argv[0], " game_id turn_number [/path/to/games.db]"
    print "\tEx:", argv[0], " 4 26b ./games.db"


if __name__ == "__main__":
    if len(argv) < 3:
        usage()
    else:
        game_id = argv[1]
        turn_number = argv[2]
        gamedb = len(argv) > 3 and argv[3] or "./games.db"

        t0 = time.time()
        db = GameDB(gamedb)
        board = db.retrieveBoard(game_id, turn_number)
        print board
        print "DB connection + retrieval time =", time.time() - t0, "seconds."

        t0 = time.time()
        aggro = score(board)
        print "Aggro calculation time =", time.time() - t0, "seconds."
        aggro_str = ""
        for row in aggro:
            for val in row:
                aggro_str += ("%.2f\t" % (val)).rjust(6)
            aggro_str += "\n"

        show_colored(board, aggro)

        print aggro_str

        for piece in board.pieces:
            if frozen(piece, board):
                print piece, "is frozen."
            print piece, "mobility =", mobility(piece, board)



