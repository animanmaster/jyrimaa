
class Direction:
    NORTH = 'n'
    SOUTH = 's'
    WEST  = 'w'
    EAST  = 'e'
    DEAD  = 'x' #kind of a hack-job...

    REVERSE = {     NORTH : SOUTH,
                    SOUTH : NORTH,
                    WEST  : EAST,
                    EAST  : WEST,
                    DEAD  : DEAD} #kind of a hack-job...

    OFFSET = {    NORTH : (1, 0),
                  WEST  : (0, -1),
                  EAST  : (0, 1),
                  SOUTH : (-1, 0),
                  DEAD  : (0, 0)} #kind of a hack-job...

    
