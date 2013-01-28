
from gamedb import *

def all_moves(db):
    for movelist in db.query('select movelist from games'):
        yield movelist

class Turn:
    def __init__(self, turn_string):
        moves = turn_string.split(' ')
        self.turn_id = moves[0]
        self.moves = moves[1:]

    def __str__(self):
        return "[{0}] {1}\n".format(self.turn_id, self.moves)


from ctypes import *

class PieceData(Structure):
    distance_array = lambda size: (c_ubyte * size)
    _fields_ = [
        ('piece', c_char),  # the piece character (like 'r')
        ('location', c_char_p), # the piece location (like 'a8')
        ('stronger_distances', distance_array(14)), # each byte has num_friends|num_enemies at the index's distance.
        ('weaker_distances', distance_array(14)), # same as above, but for weaker pieces.
        ('trap_distances', distance_array(4)), # how far each trap is, sorted by closest.
        ('boundary_distances', distance_array(4)) # how far the n, w, s, e boundaries are.
    ]

    
    def combine_byte_strings(self, size, *args):
        base = ''
        for arg in args:
            base += base + string_at(addressof(arg), sizeof(c_byte * size))
        return base

    def combine_four_byte_strings(self, *args):
      return self.combine_byte_strings(4, *args)

    def get_filtered_state(self):
        return self.combine_four_byte_strings(self.stronger_distances,
                                         self.weaker_distances,
                                         self.trap_distances) #should we look at boundaries, too?

PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r', None)
AGGRO  = ( 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1, 0)

TRAPS = ((2,2), (2,5), (5,2), (5,5))

PIECE_AGGRO = dict(zip(PIECES, AGGRO))

def is_stronger_than(piece, otherpiece):
    return otherpiece and abs(PIECE_AGGRO[otherpiece.char]) > abs(PIECE_AGGRO[piece.char])

Piece.is_stronger_than = is_stronger_than

def distance(position1, position2): #just a convenience thang.
    '''The distance between two position objects.'''
    return abs(position1.row - position2.row) + abs(position1.col - position2.col)

# distance = max of 3 bits (max distance is 8), 16 pieces total. 3 * 16 = 48 bits + 12 (for 4 traps) = 60 with 4 bits left over for whatever.
def distance_map(board):
    dist_map = {}
    for piece in board.pieces:
        dist_map[piece] = {}
        for otherpiece in board.pieces:
            dist_map[piece][otherpiece] = distance(piece.position, otherpiece.position)
    return dist_map

TRAPS = (Position(2,2), Position(2,5), Position(5,2), Position(5,5))

def c_ubyteify(array):
    return (c_ubyte * len(array))(*array)

def get_piece_data(board):
    data = []
    for piece in board.pieces:
        stronger_distances = [0] * 14
        weaker_distances = [0] * 14
        trap_distances = [distance(piece.position, trap) for trap in TRAPS]
        trap_distances.sort() # Should the specific trap we're talking about matter, or is it just the distance to a trap that matters?
        boundary_distances = [piece.position.col, 7 - piece.position.col, piece.position.row, 7 - piece.position.row]
        for otherpiece in board.pieces:
            piece_dist = distance(piece.position, otherpiece.position) - 1
            if piece_dist: # not 0 (i.e. not itself)
                dists = piece.is_stronger_than(otherpiece) and weaker_distances or stronger_distances
                # Update the count of weaker/stronger pieces this distance away accounting for this other piece.
                # The first half of the byte counts friends, the second half counts enemies.
                # So to add 1 friend to 0000 0000, you have to add 0001 0000 = 16 to get 0001 0000
                # To add 1 enemy to 0000 0000, you have to add 0000 0001 = 1 to get 0000 0001
                dists[piece_dist] += (piece.friend_of(otherpiece) and 16 or 1)
        #import pdb; pdb.set_trace()
        data.append(
            PieceData(piece.char, 
                      str(piece.position),
                      c_ubyteify(stronger_distances),
                      c_ubyteify(weaker_distances),
                      c_ubyteify(trap_distances),
                      c_ubyteify(boundary_distances)
                    )
            )
    return data

def note(noted, game_id, turn_id, piece_data):
    for pd in piece_data:
        string = pd.get_filtered_state()
        data = "{0} {1} {2}{3}".format(game_id, turn_id, pd.piece, pd.location)
        if string in noted:
            noted[string].add(data)
        else:
            noted[string] = set([data])
        

## {{{ http://code.activestate.com/recipes/65287/ (r5)
# code snippet, to be included in 'sitecustomize.py'
import sys

def info(type, value, tb):
   # if hasattr(sys, 'ps1') or not sys.stderr.isatty():
   #    # we are in interactive mode or we don't have a tty-like
   #    # device, so we call the default hook
   #    sys.__excepthook__(type, value, tb)
   # else:
  import traceback, pdb
  # we are NOT in interactive mode, print the exception...
  traceback.print_exception(type, value, tb)
  print
  # ...then start the debugger in post-mortem mode.
  pdb.pm()

sys.excepthook = info
## end of http://code.activestate.com/recipes/65287/ }}}



db = GameDB('./games.db')
#outfile = open('./gamestates.out', 'a')
encountered = {}
num_games = 0
for result_set in db.query('select * from games where movelist not like "%takeback%" and movelist not like "%resign%" limit 20'):
    num_games += 1
    game_id = result_set[0]
    print "Examining game", game_id
    movelist = result_set[-1]
    turns = movelist.split("\\n")
    board = db.build_board_from_turns(turns, '2w')

    turnNum = board.turn_index
#    print "Turns:", turns
#    print "Board:", board
    piece_data = get_piece_data(board)
    #import pdb; pdb.set_trace()
    note(encountered, game_id, '1b', piece_data)
    for turn in turns[turnNum:]:
        moves = db.get_moves(turn)
        turn_id = moves.pop(0)
        for move in moves:
            if move == 'takeback':
                db.takeback(turns[turnNum - 1])
            else:
                board.apply_move(Move(move))
                note(encountered, game_id, turn_id, get_piece_data(board))
        turnNum += 1
        #print "Board at ", turn_id, board
for value in encountered:
    same_piece_position = set()
    actual = set()
    for similar in encountered[value]:
        splitted = similar.split()
        splitsearch = "{0} {1}".format(splitted[1], splitted[2])
        if not splitsearch in same_piece_position:
            same_piece_position.add(splitsearch)
        else:
            actual.add(similar)

    if len(actual) > 1:
        print "%s:" % value.encode('hex')
        print "\t", encountered[value]

print "Examined", num_games, "games"

