#!/usr/bin/env python
#import sqlite3
from java.lang import *
from java.sql import *
from board import *

#TODO: Optimize! Too many inefficiencies out of laziness. :P

class GameDB:

    def __init__(self, strDb):
        if strDb:
#            self.conn = sqlite3.connect(strDb)
#            self.cursor = self.conn.cursor()
            Class.forName("org.sqlite.JDBC");
            self.dbfile = strDb
            self.conn = DriverManager.getConnection("jdbc:sqlite:" + strDb)
            self.stat = self.conn.createStatement()
        else:
            raise ValueError("No valid db provided!")

    def get_movelist(self, gameID):
#        return str(self.cursor.execute("select movelist from games where id=?", (gameID,)).fetchone()[0])
        return str(self.stat.executeQuery("select movelist from games where id=" + str(gameID)).getString("movelist"))

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

