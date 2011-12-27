# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Malik Ahmed"
__date__ ="$Dec 26, 2011 2:33:58 AM$"


'''Map column index to column letter'''
COLS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

def convert(strPos):
    '''Convert a string position to a row, col pair'''
    return int(strPos[1]) - 1, COLS.index(strPos.lower()[0])

def make_position(row, col):
    '''Take a row, col pair and return the string representation'''
    return COLS[col] + str(row + 1)

class Direction:
    NORTH = 'n'
    SOUTH = 's'
    WEST  = 'w'
    EAST  = 'e'
    DEAD  = 'x' #kind of a hack-job...

def make_move(piece, position, direction):
    return Move(piece + position + direction)


class Move:
    DIR_REVERSE = { Direction.NORTH : Direction.SOUTH,
                    Direction.SOUTH : Direction.NORTH,
                    Direction.WEST  : Direction.EAST,
                    Direction.EAST  : Direction.WEST,
                    Direction.DEAD  : Direction.DEAD} #kind of a hack-job...

    DIR_OFFSET = {Direction.NORTH : (1, 0),
                  Direction.WEST  : (0, -1),
                  Direction.EAST  : (0, 1),
                  Direction.SOUTH : (-1, 0),
                  Direction.DEAD  : (0, 0)} #kind of a hack-job...

    def __init__(self, move):
        '''
        Construct a Move object from the given move in Arimaa notation e.g. "ra5n"
        '''
        self.move = move
        self.piece, self.old_position, self.direction, self.new_position = self.get_move_details(move)

    def reverse(self):
        return make_move(self.piece, self.new_position, Move.DIR_REVERSE[self.direction])

    def get_new_position(self, position, direction):
        row, col = convert(position)
        row_offset, col_offset = Move.DIR_OFFSET[direction]
        return make_position(row + row_offset, col + col_offset)

    def get_move_details(self, move):
        piece = move[0]
        position = move[1:3]
        direction = move[3]
        new_position = self.get_new_position(position, direction)
        return piece, position, direction, new_position

class Position:
    def __init__(self, row, col):
        self.row, self.col = row, col

    def __str__(self):
        return make_position(self.row, self.col)

class Piece:
    def __init__(self, char, position):
        self.char = str(char)[0]
        self.position = position

    def __str__(self):
        return str(self.char) + str(self.position)

class Board:

    def __init__(self):
        '''Constructor: initialize the interal 2D array.'''
        self.spots = [[None] * 8 for i in range(8)]
        self.pieces = []

    def place(self, piece, strPos):
        '''Place the given piece at the provided position (like "A4")'''
        row, col = convert(strPos)
        if isinstance(piece, str):
            piece = Piece(piece, Position(row, col))

        oldpiece = self.spots[row][col] #Hopefully this is None since we're removing it from the board.
        self.spots[row][col] = piece
        piece.position.row, piece.position.col = row, col
        self.pieces.append(piece)
        return oldpiece

    def get_piece(self, pos):
        '''Return whatever is at the spot given by this position'''
        row, col = convert(pos)
        return self.spots[row][col]


    def clear(self, position):
        '''Remove anything that may be on this spot'''
        row, col = convert(position)
        piece = self.spots[row][col]
        self.spots[row][col] = None
        if piece:
            #self.piece_map[piece] = None
            self.pieces.remove(piece)
        return piece


    def apply_move(self, move):
        '''Apply a Move object to this board.'''
        oldpiece = self.get_piece(move.old_position)

        if oldpiece.char != move.piece:
            raise ValueError("Invalid move: the piece {0} is not at position {1}".format(piece, move.old_position))

        if move.direction != Direction.DEAD and self.get_piece(move.new_position):
            raise ValueError("Illegal move: a piece is on the new position {0}".format(move.new_position))

        piece = self.clear(move.old_position)
        if move.direction != Direction.DEAD:
            self.place(piece, move.new_position)

    def undo_move(self, move):
        '''Reverse a move and apply it.'''
        self.apply_move(move.reverse())

    def __str__(self):
        '''Equivalent of Java toString()'''
        col_header = "  a b c d e f g h \n"
        line       = "  --------------- \n"
        board_str = "\n" + col_header + line
        for i in range(8, 0, -1):
            row = self.spots[i-1]
            board_str += str(i) + "|"
            for piece in row:
                board_str += ((piece and piece.char) or " ") + "|"
            board_str += str(i) + "\n" + line
        board_str += col_header
        return board_str

    def __getitem__(self, index):
        return self.spots[index]
