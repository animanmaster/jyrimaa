from position import *

def make_move(piece, position, direction):
    return Move(str(piece) + str(position) + str(direction))

class Move:

    def __init__(self, move):
        '''
        Construct a Move object from the given move (either in Arimaa notation e.g. "ra5n" or as a Move object)
        '''
        self.move = str(move)
        self.piece, self.old_position, self.direction, self.new_position = self.get_move_details(move)

    def reverse(self):
        return make_move(self.piece, self.new_position, DIR_REVERSE[self.direction])

    def get_new_position(self, position, direction):
        row_offset, col_offset = DIR_OFFSET[direction]
        return Position(position.row + row_offset, position.col + col_offset)

    def get_move_details(self, move):
        piece = move[0]
        position = str_to_pos(move[1:3])
        direction = move[3]
        new_position = self.get_new_position(position, direction)
        return piece, position, direction, new_position

    def __str__(self):
        return str(piece) + str(position) + str(direction)

