#!/usr/bin/env python

try:
    from java.lang import *
    from java.sql import *
    USING_JAVA = True
except ImportError:
    import sqlite3
    USING_JAVA = False

from board import *

class EndOfGameError(Exception):
    pass

#TODO: Optimize! Too many inefficiencies out of laziness. :P
class GameDB:

    def __init__(self, strDb):
        if strDb:
            self.dbfile = strDb
            if USING_JAVA:
                Class.forName("org.sqlite.JDBC");
                self.conn = DriverManager.getConnection("jdbc:sqlite:" + strDb)
                self.cursor = None
                self.stat = self.conn.createStatement()
            else:
               self.conn = sqlite3.connect(strDb)
               self.cursor = self.conn.cursor()
               self.stat = None
        else:
            raise ValueError("No valid db provided!")

    def query(self, sql, args=()):
        if self.cursor:
            # sqlite3
            return self.cursor.execute(sql, args)
        else:
            # sqlite-jdbc
            # TODO - figure out how to make prepared statments work similar to sqlite3 above
            return self.stat.executeQuery(sql)

    def get_movelist(self, gameID):
        base_query = "select movelist from games where id="
        if self.cursor:
            return str(self.cursor.execute(base_query + "?", (gameID,)).fetchone()[0])
        else:
            return str(self.stat.executeQuery(base_query + str(gameID)).getString("movelist"))

    def get_moves(self, turn):
        return turn.split(" ")

    def takeback(self, turn):
        for move in self.get_moves(turn)[1:]:
            self.board.undo_move(Move(move))

    def build_board_from_turns(self, turns, turnID):
        self.board = Board()
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
                    elif move:
                        self.board.place(str(move[0]), move[1:])
                turnNum += 1

        #Apply moves
        setting_up = True
        while setting_up:
            moves = self.get_moves(turns[turnNum])
            turn_id = moves.pop(0)

            if turn_id == turnID:
                setting_up = False
                self.board.moves = moves
            else:
                for move in moves:
                    #print "Applying", move
                    if move == "takeback":
                        #undo last turn
                        self.takeback(turns[turnNum - 1])
                    else:
                        self.board.apply_move(Move(move))
                turnNum += 1
        
        self.board.turn_index = turnNum
        return self.board

    #TODO: This method needs to be cleaned up a bit. Too much repeated code.
    #      Also, handle the case where we only want the setup.
    def retrieveBoard(self, gameID, turnID):
        turns = self.get_movelist(gameID).split("\\n")
        return self.build_board_from_turns(turns, turnID)


    #TODO: This method needs to be cleaned up a bit. Too much repeated code.
    #      Also, handle the case where we only want the setup.
    def retrieveAEIBoard(self, gameID, turnID):
        from aei.pyrimaa import board as aei_board
        turns = self.get_movelist(gameID).split("\\n")
        last_board = None
        current_board = aei_board.Position(aei_board.Color.GOLD, 4, aei_board.BLANK_BOARD)
        turn_id = ''
        for turn in turns:
            split_index = turn.find(' ')
            if split_index == -1:
                turn_id, moves = turn.strip(), ''
            else:
                turn_id, moves = turn[0:split_index+1].strip(), turn[split_index+1:].strip()

            if moves == 'takeback':
                current_board = last_board
            elif turn_id == turnID:
                return current_board
            elif not moves:
                raise EndOfGameError('No moves for turn %s' % turn_id)
            else:
                last_board = current_board
                try:
                    current_board = current_board.do_move_str(moves)
                except:
                    print "turn_id: %s, moves: %s" % (turn_id, moves)
                    raise
        else:
            raise ValueError('Could not find turnID %s in gameID %s' % (turnID, gameID))

