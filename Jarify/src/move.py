from position import *
from direction import *

class Move:
    def __init__(self, move):
        '''
        Construct a Move object from the given move in Arimaa notation e.g. "ra5n"
        '''
        self.move = move
        self.piece, self.old_position, self.direction, self.new_position = self.get_move_details(move)

    def reverse(self):
        return Move(self.piece + self.new_position + Direction.REVERSE[self.direction])

    def get_new_position(self, position, direction):
        row, col = convert(position)
        row_offset, col_offset = Direction.OFFSET[direction]
        return make_position(row + row_offset, col + col_offset)

    def get_move_details(self, move):
        piece = move[0]
        position = move[1:3]
        direction = move[3]
        new_position = self.get_new_position(position, direction)
        return piece, position, direction, new_position

