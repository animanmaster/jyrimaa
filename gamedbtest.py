from gamedb import *

b = Board()
print b

b.place("r", "A1")
b.place("E", "A2")

print b

move = Move("ra1e")
b.apply_move(move)
print b

b.undo_move(move)
print b

db = GameDB("./games.db")
board = db.retrieveBoard(4, "26b")
print board

print board.piece_map
