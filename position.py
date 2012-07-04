
'''Map column index to column letter'''
COLS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

def convert(strPos):
    '''Convert a string position to a row, col pair'''
    return int(strPos[1]) - 1, COLS.index(strPos.lower()[0])

def make_position(row, col):
    '''Take a row, col pair and return the string representation'''
    return COLS[col] + str(row + 1)

def distance(position1, position2): #just a convenience thang.
    '''The distance between two position objects.'''
    return abs(position1.row - position2.row) + abs(position1.col - position2.col)


class Position:
    def __init__(self, row, col):
        self.row, self.col = row, col

    @staticmethod
    def is_this_a_trap(row, col):
        return ((row == 2 or row == 5) and (col == 2 or col == 5))

    def is_a_trap(self):
        return Position.is_this_a_trap(self.row, self.col)

    def distance(self, position2): 
        return distance(self, position2)

    def __cmp__(self, other):
        row_diff = self.row - other.row
        col_diff = self.col - other.col

        #If on the same row, return the column difference. In either case, if this piece is "before" the other piece, this piece is "less than" the other piece.
        return row_diff or col_diff 

    def __str__(self):
        return make_position(self.row, self.col)

