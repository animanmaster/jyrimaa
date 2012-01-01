from gamedb import *
from visualize import *

PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r')
AGGRO  = ( 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1)

TRAPS = ((2,2), (2,5), (5,2), (5,5))

PIECE_AGGRO = dict(zip(PIECES, AGGRO))

def forever_alone(piece, board):
    row, col = piece.position.row, piece.position.col
    above, below, left, right = board.surrounding_pieces(row, col)
    return not (piece.friend_of(above) or piece.friend_of(below) or piece.friend_of(left) or piece.friend_of(right)) #no friends around you? Forever alone. :')

def frozen(piece, board):
    row, col = piece.position.row, piece.position.col
    myaggro = abs(PIECE_AGGRO[piece.char])
    no_friends = forever_alone(piece, board)
    isfrozen = False

    if no_friends:

        def other_piece_is_stronger(otherpiece):
            return otherpiece and abs(PIECE_AGGRO[otherpiece.char]) > myaggro

        isfrozen = (row > 0 and other_piece_is_stronger(board[row - 1][col])) or \
                   (row < 7 and other_piece_is_stronger(board[row + 1][col])) or \
                   (col > 0 and other_piece_is_stronger(board[row][col - 1])) or \
                   (col < 7 and other_piece_is_stronger(board[row][col + 1]))

    return isfrozen


#THOUGHT: Each spot contains values for each piece, taking into account the pieces blocking the way and pieces that could freeze you.
#TODO - Consider trap positions and capture patterns
#ANOTHER THOUGHT (RELATED TO THE TODO): The trap exudes the sum(half the power of the piece it's next to?)

# Mobility = 0 if frozen or surrounded by pieces that can't be pushed (?).
# Examine the piece's AOI?
# Higher mobility = higher freedom of movement.
def mobility(piece, board):
    pieces = board.pieces
    if frozen(piece, board):
        return 0
    
    for board_piece, position in pieces.iteritems():
        if board_piece != piece:
            pass

            

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
                    aggro_map[i][j] += float(PIECE_AGGRO[piece.char])/(dist + 1.0)
    return aggro_map


db = GameDB("games.db")
board = db.retrieveBoard(4, "26b")
print board

aggro = score(board)
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

