
from gamedb import *
from piece_data import PieceData
from turn_data import TurnData
import pdb
import cPickle as pickle

GAME_LIMIT = 500

def all_moves(db):
    for movelist in db.query('select movelist from games'):
        yield movelist

PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r', None)
AGGRO  = ( 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1, 0)
PIECE_AGGRO = dict(zip(PIECES, AGGRO))
TRAPS = (Position(2,2), Position(2,5), Position(5,2), Position(5,5))
STRENGTH_ORDER = 'EMHDCR'

def is_stronger_than(piece, otherpiece):
    return otherpiece and (STRENGTH_ORDER.index(piece.char.upper()) < STRENGTH_ORDER.index(otherpiece.char.upper()))

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


def calculate_piece_data(board, piece):
    if not isinstance(piece, Piece):
        piece = board.get_piece(piece)
    trap_distances = [distance(piece.position, trap) for trap in TRAPS]
    trap_distances.sort() # Should the specific trap we're talking about matter, or is it just the distance to a trap that matters?
    boundary_distances = [piece.position.col, 7 - piece.position.col, piece.position.row, 7 - piece.position.row]
    boundary_distances.sort()

    piece_data = PieceData()
    piece_data.piece = piece.char
    piece_data.location = str(piece.position)
    piece_data.trap_distances = trap_distances
    piece_data.boundary_distances = boundary_distances

    for otherpiece in board.pieces:
        piece_dist = distance(piece.position, otherpiece.position)# - 1
        if piece_dist > 0: # not 0 (i.e. not itself)
            # dists = piece.is_stronger_than(otherpiece) and weaker_distances or stronger_distances
            is_weaker = piece.is_stronger_than(otherpiece)
            # Update the count of weaker/stronger pieces this distance away accounting for this other piece.
            # The first half of the byte counts friends, the second half counts enemies.
            # So to add 1 friend to 0000 0000, you have to add 0001 0000 = 16 to get 0001 0000
            # To add 1 enemy to 0000 0000, you have to add 0000 0001 = 1 to get 0000 0001
            # dists[piece_dist] += (piece.friend_of(otherpiece) and 16 or 1)
            add_distance = piece.friend_of(otherpiece) and piece_data.add_friend or piece_data.add_enemy
            add_distance(is_weaker, piece_dist)
    return piece_data

Board.calculate_piece_data = calculate_piece_data

def get_piece_data(board):
    data = []
    for piece in board.pieces:
        piece_data = calculate_piece_data(board, piece)
        data.append(piece_data)
    return data

MOVED_DATA = {}

def note_moved_piece(identifier, before_piece_data, after_piece_data, move_number=0):
    if identifier not in MOVED_DATA:
        MOVED_DATA[identifier] = TurnData(identifier)
    MOVED_DATA[identifier].update(before_piece_data, after_piece_data, move_number)

PD_PER_TURN = {}
def note(noted, board, game_id, turn_id, game_data=(), moves = None):
    piece_data = get_piece_data(board)
    key = (game_id, game_data)
    if key not in PD_PER_TURN:
        PD_PER_TURN[key] = []
    PD_PER_TURN[key].append(
        (turn_id, piece_data
            #'|'.join(map(lambda pd: pd.get_filtered_state(14), piece_data))
        )
    )
    # pieces_moved = {}
    # if moves:
    #     for move in moves:
    #         pieces_moved[str(move)[0:3]] = True
    for pd in piece_data:
        string = pd.get_filtered_state()
        # if (pd.piece + pd.location) in pieces_moved:
        #     # This piece was moved in this turn
        #     note_moved_piece(game_id, turn_id, pd)
        data = "%s %s %s%s" % (str(game_id), str(turn_id), str(pd.piece), str(pd.location))
        if string in noted:
            noted[string].add(data)
        else:
            noted[string] = set([data])
  

def printInterestingThings(encountered):
    for value in encountered:
        same_piece_position = set()
        same_piece = set()
        actual = set()
        for similar in encountered[value]:
            splitted = str(similar).split()
            splitsearch = "{0} {1}".format(splitted[0], splitted[2])
            piece = str(splitted[2][0])
            if not splitsearch in same_piece_position:
                same_piece_position.add(splitsearch)
                if not piece in same_piece:
                    same_piece.add(piece)
                    actual.add(similar)

        if len(actual) > 1:
            print "%s: " % value
            # print_info_about(encountered[value])
            print "\t", actual  

def printTurnStatistics():
    turn_hashes = {}
    equivalent_moves = dict(map(lambda r: [r, 0], range(14))) # indexed by radius
    total_number_of_turns = 0
    hash_for_radius = map(lambda radius: (lambda pd: pd.get_filtered_state(radius)), range(14))
    winning_moves = {}
    win_percentages = {}
    for game_id, game_data in PD_PER_TURN:
        turns = PD_PER_TURN[game_id, game_data]
        total_number_of_turns += len(turns)
        wrating, brating, result = game_data
        ratings = dict(w=wrating, b=brating, d=0)
        for index in range(len(turns)):
            if index < len(turns) - 1:
                turn_id, before_piece_data = turns[index]
                player = turn_id[-1]
                _, after_piece_data = turns[index + 1]
                player_won = player == result
                value = (game_id, turn_id)
                for radius in range(14):
                    before_set = set(map(hash_for_radius[radius], before_piece_data))
                    after_set = set(map(hash_for_radius[radius], after_piece_data))
                    before_and_after = (str(before_set - after_set), str(after_set - before_set))
                    winner_bonus = (player_won and 1 or -1) * int(ratings[player]) * float(radius)/13.0
                    if before_and_after in turn_hashes:
                        turn_hashes[before_and_after].append(value)
                        equivalent_moves[radius] += 1
                        win_percentages[before_and_after] += int(player_won)
                        winning_moves[before_and_after] += winner_bonus
                    else:
                        turn_hashes[before_and_after] = [value]
                        win_percentages[before_and_after] = int(player_won)
                        winning_moves[before_and_after] = winner_bonus

    print 'Lemme show you some of the more interesting results I have found:'
    for before_and_after, values in turn_hashes.iteritems():
        if len(values) >= 2:
            print before_and_after, ':'
            print "\t", values

    print "Over", total_number_of_turns, "turns..."
    print "Total number of unique (before, after) hashes:", len(equivalent_moves.keys())
    print "Number of cases where turn deltas matched per radius:"
    for radius in equivalent_moves:
        value = equivalent_moves[radius]
        print "\t Radius", radius + 1, ":", value, '[', (float(value)/float(total_number_of_turns) * 100), '% ]'

    awesome_ones = set()
    print "Win percentages per unique (before, after) hash:"
    for before_and_after, number_of_wins in win_percentages.iteritems():
        percentage = float(number_of_wins)/float(len(turn_hashes[before_and_after])) * 100.0
        print percentage, "%:"
        print "\t", map(lambda x: str(x[0]) + ' ' + str(x[1]), turn_hashes[before_and_after])
        if percentage >= 50.0 and len(turn_hashes[before_and_after]) > 2:
            awesome_ones.add((before_and_after, percentage))

    print "Over 50%% win-rate and more than two examples:"
    for before_and_after, percentage in awesome_ones:
        print percentage, '%:'
        print "\t", map(lambda x: str(x[0]) + ' ' + str(x[1]), turn_hashes[before_and_after])

    print "Best plays by rating:"
    for before_and_after, rating in sorted(winning_moves.iteritems(), key=lambda x: x[-1], reverse=True):
        print rating, ':'
        print "\t", map(lambda x: str(x[0]) + ' ' + str(x[1]), turn_hashes[before_and_after])


def exportData(data_to_export):
    for filename, obj in data_to_export:
        print "Exporting hash to %s" % filename
        f = open(filename % GAME_LIMIT, 'w')
        pickle.dump(obj, f)
        f.close()


## {{{ http://code.activestate.com/recipes/65287/ (r5)
# code snippet, to be included in 'sitecustomize.py'
import sys

def info(type, value, tb):
   # if hasattr(sys, 'ps1') or not sys.stderr.isatty():
   #    # we are in interactive mode or we don't have a tty-like
   #    # device, so we call the default hook
   #    sys.__excepthook__(type, value, tb)
   # else:
  import traceback
  # we are NOT in interactive mode, print the exception...
  traceback.print_exception(type, value, tb)
  print
  # ...then start the debugger in post-mortem mode.
  pdb.pm()

if __name__ == '__main__':
    sys.excepthook = info
    ## end of http://code.activestate.com/recipes/65287/ }}}

    db = GameDB('./games.db')
    #outfile = open('./gamestates.out', 'a')
    encountered = {}
    num_games = 0
    for result_set in db.query('select id, wrating, brating, result, movelist from games where movelist not like "%takeback%" and movelist not like "%resign%" limit ' + str(GAME_LIMIT)):
        num_games += 1
        game_id, wrating, brating, result, movelist = result_set
        print "Examining game", game_id
        turns = movelist.split("\\n")
        board = db.build_board_from_turns(turns, '2w')
        game_data = (wrating, brating, result)

        turnNum = board.turn_index
        turn_id = '1b'
        for turn in turns[turnNum:]:
            moves = db.get_moves(turn)
            turn_id = moves.pop(0) or turn_id
            note(encountered, board, game_id, turn_id, game_data, moves)
            number_of_moves = len(moves)
            for move_index, move in enumerate(moves):
                if move == 'takeback':
                    db.takeback(turns[turnNum - 1])
                elif move:
                    move = Move(move)
                    before_piece_data = board.calculate_piece_data(move.old_position)
                    oldpiece, piece_moved = board.apply_move(move)
                    note_moved_piece((game_id, turn_id),
                                     before_piece_data,
                                     piece_moved and board.calculate_piece_data(move.new_position) or None,
                                     move_index + 1)

            turnNum += 1
        if game_id and turn_id:
            note(encountered, board, game_id, turn_id, game_data)

    # printInterestingThings(encountered)
    printTurnStatistics()

    print "Examined", num_games, "games"
    # exportData((
    #     ('encounteredhash%d.pickle', encountered),
    #     ('move_data%d.pickle', MOVED_DATA),
    #     # ('pd_per_turn%d.pickle', PD_PER_TURN)
    #     )
    # )
