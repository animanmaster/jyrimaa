#!/usr/bin/env python

try:
    from java.lang import *
    from java.sql import *
    USING_JAVA = True
except ImportError:
    import sqlite3
    USING_JAVA = False

from board import *

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

    def get_movelist(self, gameID):
        base_query = "select movelist from games where id="
        if self.cursor:
            return str(self.cursor.execute(base_query + "?", (gameID,)).fetchone()[0])
        else:
            return str(self.stat.executeQuery(base_query + str(gameID)).getString("movelist"))

    def get_moves(self, turn):
        return turn.split(" ")

    def takeback(self, turn):
        for move in self.get_moves(turn):
            self.board.undo_move(Move(move))

    #TODO: This method needs to be cleaned up a bit. Too much repeated code.
    #      Also, handle the case where we only want the setup.
    def retrieveBoard(self, gameID, turnID):
        self.board = Board()
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
                        self.board.place(move[0], move[1:])
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
                        self.board.apply_move(Move(move))
                turnNum += 1

        return self.board

