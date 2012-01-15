from gamedb import *

def colorizer(value, i = None, j = None):
    #scaling it by 4 so that the colors are more discernible
    scale_factor = 4
    value *= scale_factor
    default = 0
    return Color((value > 0) and bounded(255 - value) or default,
                  default,
                  (value < 0) and bounded(255 + value) or default)


def score(board):
    PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r', None)
    AGGRO  = ( 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1, 0)
    TRAPS = (Position(2,2), Position(2,5), Position(5,2), Position(5,5))
    PIECE_AGGRO = dict(zip(PIECES, AGGRO))  #maps each piece in PIECES to the corresponding value in AGGRO.

    def forever_alone(piece):
        row, col = piece.position.row, piece.position.col
        above, below, left, right = board.surrounding_pieces(row, col)
        return not (piece.friend_of(above) or piece.friend_of(below) or piece.friend_of(left) or piece.friend_of(right)) #no friends around you? Forever alone. :')

    def frozen(piece):
        row, col = piece.position.row, piece.position.col
        myaggro = abs(PIECE_AGGRO[piece.char])
        no_friends = forever_alone(piece)
        isfrozen = False

        if no_friends:

            def other_piece_is_stronger(otherpiece):
                return otherpiece and abs(PIECE_AGGRO[otherpiece.char]) > myaggro

            isfrozen = (row > 0 and other_piece_is_stronger(board[row - 1][col])) or \
                       (row < 7 and other_piece_is_stronger(board[row + 1][col])) or \
                       (col > 0 and other_piece_is_stronger(board[row][col - 1])) or \
                       (col < 7 and other_piece_is_stronger(board[row][col + 1]))

        return isfrozen


    #THOUGHT: Each spot contains values for each piece, taking into account the pieces blocking the way and pieces that could freeze you.
    # 	(kinda like a "perspective" for each piece at each spot on the board).
    #TODO - Consider trap positions and capture patterns
    #ANOTHER THOUGHT (RELATED TO THE TODO): The trap exudes the sum(half the power of the piece it's next to?)

    # Mobility = 0 if frozen or surrounded by pieces that can't be pushed (?).
    # Examine the piece's AOI?
    # Higher mobility = higher freedom of movement.
    def mobility(piece):
        pieces = board.pieces
        mobility = 0
        row, col = piece.position.row, piece.position.col
        if frozen(piece):
            return mobility
        above, below, left, right = board.surrounding_pieces(row, col)
        if above and below and left and right:
            return mobility #there are pieces all around, can't move.
        #TODO count the number of paths available rather than just free spots within 4 spaces.
        for rowOffset in range(-4, 4):
            whatsleft = 4 - abs(rowOffset)
            for colOffset in range(-whatsleft, whatsleft + 1):
                if 0 <= row + rowOffset <= 7 and 0 <= col + colOffset <= 7 and not board.find_piece(row + rowOffset, col + colOffset):
                    mobility += 1 #found an empty spot in my mobility range
        
        return mobility


    def trap_influence(position):
        influence = 0.0
        for trap in TRAPS:
            if distance(position, trap) <= 2:	#We don't really care about anything further since you can't be pushed/pulled.
                neighboring_pieces = board.surrounding_pieces(position.row, position.col)
                for piece in neighboring_pieces:
                    influence += PIECE_AGGRO[piece and piece.char or None]/4
        return influence
            
    def explore(row, col, resources_left, initial = True):
        piece_exists = board.find_piece(row, col)
        count = 0 if (initial or piece_exists) else 1
        if initial or (resources_left and not piece_exists):
            resources_left -= 1
            count += explore(row - 1, col, resources_left, False)   #below
            count += explore(row, col - 1, resources_left, False)   #left
            count += explore(row, col + 1, resources_left, False)   #right
            count += explore(row + 1, col, resources_left, False)   #above
        return count
            

# ACTUAL SCORING HAPPENS HERE:
# def score(board):
    #stuff
    # first pass: distance from pieces
    # second pass: ???

    aggro_map = [ [0] * 8 for i in range(8) ]
    pieces = board.pieces
    for i in range(8):
        for j in range(8):
            current_pos = Position(i, j)
            for piece in pieces:
                dist = distance(current_pos, piece.position)
                if dist <= 4:
                    aggro_map[i][j] += float(PIECE_AGGRO[piece.char])/(dist + 1.0) #+ trap_influence(current_pos)
    #Give each piece a mobility
    most_mobile, most_mobility = None, 0
    for piece in pieces:
        row = piece.position.row
        col = piece.position.col
        piece.mobility = explore(row, col, 4) #mobility(piece)
        print piece, piece.mobility
        if piece.mobility >= most_mobility:
            most_mobile = piece
            most_mobility = piece.mobility
    print "Most mobile piece: ", most_mobile
    
    # Return the scored board
    return aggro_map

