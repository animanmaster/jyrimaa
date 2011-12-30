
'''Map column index to column letter'''
COLS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

def convert(strPos):
    '''Convert a string position to a row, col pair'''
    return int(strPos[1]) - 1, COLS.index(strPos.lower()[0])

def make_position(row, col):
    '''Take a row, col pair and return the string representation'''
    return COLS[col] + str(row + 1)

class Position:
    def __init__(self, row, col):
        self.row, self.col = row, col

    def __str__(self):
        return make_position(self.row, self.col)

