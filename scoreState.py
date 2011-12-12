from gamedb import *
import sys


PIECES = ['E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r']
AGGRO  = [ 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1]

PIECE_AGGRO = dict(zip(PIECES, AGGRO))

def distance(position1, position2):
    return abs(position1.row - position2.row) + abs(position1.col - position2.col)

#THOUGHT: Each spot contains values for each piece, taking into account the pieces blocking the way and pieces that could freeze you.

def score(board):
    #stuff
    # first pass: distance from pieces
    # second pass: ???
    aggro_map = [ [0] * 8 for i in range(8) ]
    pieces = board.pieces
    for i in range(8):
        for j in range(8):
            current_pos = Position(i, j)
            for piece in pieces:
                dist = distance(current_pos, piece.position)
                if dist <= 4:
                    aggro_map[i][j] += PIECE_AGGRO[piece.char]/(dist + 1)
    return aggro_map



db = GameDB("./games.db")
board = db.retrieveBoard(4, "26b")
print board

aggro = score(board)
aggro_str = ""
for row in aggro:
    for val in row:
        aggro_str += ("%.2f\t" % (val)).rjust(6)
    aggro_str += "\n"

print aggro_str

