from collections import namedtuple

'''Map column index to column letter'''
COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def convert(pos):
    '''Convert a string position (like A5) to a row, col pair for internal use (like (4, 0))'''
    if isinstance(pos, Position):
        return pos.row, pos.col
    elif isinstance(pos, str):
        return (int(pos[1]) - 1, COLS.index(pos.upper()[0]))
    else:
        raise TypeError("convert can only convert a string or Position object into a row and column.")

def str_notation(row, col):
    '''Take a row, col pair and return the string representation'''
    return COLS[col] + str(row + 1)

class Position:
    def __init__(self, strPos):
        self.row, self.col  = convert(strPos)

    def __str__(self):
        return str_notation(self.row, self.col)


class Direction:
    NORTH = 'n'
    SOUTH = 's'
    WEST  = 'w'
    EAST  = 'e'
    DEAD  = 'x' #kind of a hack-job...

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


