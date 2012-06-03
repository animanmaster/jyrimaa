# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Malik Ahmed"
__date__ ="$Dec 26, 2011 2:33:58 AM$"

from position import *
from direction import *
from move import *
from piece import *

def its_a_trap(row, col):
    return Position.is_this_a_trap(row, col)

class Board:
    '''The board. Most of the public methods take strings to be directly accessible from AEI and for human consumption.'''

    def __init__(self):
        '''Constructor: initialize the interal 2D array.'''
        self.spots = [[None] * 8 for i in range(8)]
        self.pieces = []

    def find_piece(self, row, col):
        '''Return the piece at row, col or None if out of bounds.'''
        return (0 <= row <= 7 and 0 <= col <= 7 and self[row][col]) or None 

    def surrounding_pieces(self, row, col):
        '''Return the pieces above, below, left, and, right of the spot (row, col).'''
        return self.find_piece(row + 1, col), self.find_piece(row - 1, col), self.find_piece(row, col - 1), self.find_piece(row, col + 1)

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
        #TODO shouldn't have to distinguish between a placement and a move.
        if move.direction == Direction.ALIVE:
            self.place(move.piece, move.old_position)
        else: 
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
        '''Allows us to use [] on a board.'''
        return self.spots[index]

