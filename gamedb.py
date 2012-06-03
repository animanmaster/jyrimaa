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
        moves = self.get_moves(turn)
        print "Taking back", moves.pop(0), moves
        moves.reverse()
        print "Ordered:", moves
        for move in moves:
            self.board.undo_move(Move(move))

    #TODO: This method needs to be cleaned up a bit. Too much repeated code.
    #      Also, handle the case where we only want the setup.
    def retrieveBoard(self, gameID, turnID):
        self.board = Board()
        turns = self.get_movelist(gameID).split("\\n")
        turnNum = 0

        if int(turnID[0]) * (turnID[1] == 'w' and 1 or 2) > len(turns):
            raise ValueError("Turn ID exceeds number of turns for Game %d" % gameID)

        done = False
        
        def is_placement(move):
            return len(move) == 3 #e.g. ra3

        while turnNum < len(turns) and not done:
            moves = self.get_moves(turns[turnNum])
            turn_id = moves.pop(0)
            if turn_id == turnID:
                done = True
            else:
                for move in moves:
                    if move == "takeback":
                        #undo last turn
                        self.takeback(turns[turnNum - 1])
                    elif is_placement(move):
                        #Place initial pieces
                        self.board.place(move[0], move[1:])
                    else:
                        #Apply moves
                        self.board.apply_move(Move(move))
                turnNum += 1

        if not done:
            raise ValueError("Invalid Turn ID provided.")
        
        return self.board

