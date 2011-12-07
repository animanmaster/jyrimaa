from gamedb import *

def score(board):
    #stuff



db = GameDB("./games.db")
board = db.retrieveBoard(4, "26b")
print board

score(board)

