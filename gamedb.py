#!/usr/bin/env python
import sqlite3

#TODO: Optimize! Too many inefficiencies out of laziness. :P

'''Map column index to column letter'''
COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def convert(strPos):
    '''Convert a string position to a row, col pair'''
    return int(strPos[1]) - 1, COLS.index(strPos.upper()[0])

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



class Board:

    def __init__(self):
        '''Constructor: initialize the interal 2D array.'''
        self.__spots = [[None] * 8 for i in range(8)]

    def place(self, piece, strPos):
        '''Place the given piece at the provided position (like "A4")'''
        row, col = convert(strPos)
        oldpiece = self.__spots[row][col]
        self.__spots[row][col] = piece
        return oldpiece

    def get_piece(self, pos):
        '''Return whatever is at the spot given by this position'''
        row, col = convert(pos)
        return self.__spots[row][col]


    def clear(self, position):
        '''Remove anything that may be on this spot'''
        row, col = convert(position)
        self.__spots[row][col] = None
    

    def apply_move(self, move):
        '''Apply a Move object to this board.'''
        oldpiece = self.get_piece(move.old_position)
        
        if oldpiece != move.piece:
            raise ValueError("Invalid move: the piece {0} is not at position {1}".format(piece, move.old_position))
        
        if move.direction != Direction.DEAD and self.get_piece(move.new_position):
            raise ValueError("Illegal move: a piece is on the new position {0}".format(move.new_position))

        self.clear(move.old_position)
        if move.direction != Direction.DEAD:
            self.place(move.piece, move.new_position)

    def undo_move(self, move):
        '''Reverse a move and apply it.'''
        self.apply_move(move.reverse())

    def __str__(self):
        '''Equivalent of Java toString()'''
        col_header = "  a b c d e f g h \n"
        line       = "  --------------- \n"
        board_str = "\n" + col_header + line
        for i in range(8, 0, -1):
            row = self.__spots[i-1]
            board_str += str(i) + "|"
            for piece in row:
                board_str += (piece or " ") + "|"
            board_str += str(i) + "\n" + line
        board_str += col_header
        return board_str


class GameDB:

    def __init__(self, strDb):
        if strDb:
            self.conn = sqlite3.connect(strDb)
            self.cursor = self.conn.cursor()
        else:
            raise ValueError("No valid db provided!")

    def get_movelist(self, gameID):
        return str(self.cursor.execute("select movelist from games where id=?", (gameID,)).fetchone()[0])

    def get_moves(self, turn):
        return turn.split(" ")

    def takeback(self, turn):
        for move in self.get_moves(turn):
            board.undo_move(Move(move))

    #TODO: This method needs to be cleaned up a bit. Too much repeated code.
    def retrieveBoard(self, gameID, turnID):
        board = Board()
        turns = self.get_movelist(gameID).split("\\n")
        turnNum = 0
        setting_up = True

        #Place initial pieces
        while setting_up:
            moves = self.get_moves(turns[turnNum])
            turn_id = moves.pop(0) #gives us the turn number and player color e.g. "1w"

            if int(turn_id[0]) > 1:
                setting_up = False
            else:
                for move in moves:
                    if move == "takeback":
                        #undo last turn
                        self.takeback(turns[turnNum - 1])
                    else:
                        board.place(move[0], move[1:])
                turnNum += 1

        #Apply moves
        setting_up = True
        while setting_up:
            moves = self.get_moves(turns[turnNum])
            turn_id = moves.pop(0)

            if turn_id == turnID:
                setting_up = False
            else:
                for move in moves:
                    #print "Applying", move
                    if move == "takeback":
                        #undo last turn
                        self.takeback(turns[turnNum - 1])
                    else:
                        board.apply_move(Move(move))
                turnNum += 1

        return board

