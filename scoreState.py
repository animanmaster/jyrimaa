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
    SILVER_PIECES = ('e', 'm', 'h', 'd', 'c', 'r')
    GOLD_PIECES = ('E', 'M', 'H', 'D', 'C', 'R') 
    PIECES = GOLD_PIECES + SILVER_PIECES + (None,)
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
            dist = distance(position, trap)
            if dist <= 2:	#We don't really care about anything further since you can't be pushed/pulled.
                neighboring_pieces = board.surrounding_pieces(position.row, position.col)
                for piece in neighboring_pieces:
                    influence += PIECE_AGGRO[piece and piece.char or None]/((dist + 1.0) ** 2)
        return influence
            
    def explore(piece, row, col, resources_left, initial = True):
        piece_exists = board.find_piece(row, col)
        count = 0 if (initial or piece_exists) else 1
        if initial or (resources_left and not piece_exists):
            resources_left -= 1
            if piece.char != 'R':   #Gold rabbits can't move backwards.
                count += explore(piece, row - 1, col, resources_left, False)   #below
            count += explore(piece, row, col - 1, resources_left, False)   #left
            count += explore(piece, row, col + 1, resources_left, False)   #right
            if piece.char != 'r':   #Silver rabbits can't move backwards.
                count += explore(piece, row + 1, col, resources_left, False)   #above
        #else see if you can push/pull?
        return count

    def is_gold(piece):
        return piece.char.isupper()

    def is_silver(piece):
        return piece.char.islower()

    def insert(arr, value, compare):
        if len(arr) == 0:
            arr.append(value)
        else:
            # TODO binary search for index, then insert.
            i = 0
            while i < len(arr) and compare(value, arr[i]) < 0:
                i += 1
            if i == len(arr):
                arr.append(value)
            else:
                rest = arr[i:]
                arr[i] = value
                arr[i+1:] = rest

    # distance = max of 3 bits (max distance is 8), 16 pieces total. 3 * 16 = 48 bits + 12 (for 4 traps) = 60 with 4 bits left over for whatever.
    def distance_map():
        dist_map = {}
        for piece in board.pieces:
            dist_map[piece] = {}
            for otherpiece in board.pieces:
                dist_map[piece][otherpiece] = distance(piece.position, otherpiece.position)
        return dist_map

    def decide(aggro):
        pieces_in_danger = []
        safest_gold_spots = []
        safest_silver_spots = []

        for piece in board.pieces:
            row, col = piece.position.row, piece.position.col
            spot_value = aggro[row][col]
            if (is_gold(piece) and spot_value < 0) or (is_silver(piece) and spot_value > 0): #and abs(spot_value) >= PIECE_AGGRO(piece.char)
                pieces_in_danger.append(piece)
        
        print "In Danger:", [str(piece) for piece in pieces_in_danger]
        
        most_positive_first = lambda v1, v2: aggro[v1.row][v1.col]-aggro[v2.row][v2.col]
        most_negative_first = lambda v1, v2: -most_positive_first(v1, v2)

        for row in range(8):
            for col in range(8):
                if aggro[row][col] >= 0:
                    insert(safest_gold_spots, Position(row,col), most_positive_first)
                if aggro[row][col] <= 0:
                    insert(safest_silver_spots, Position(row,col), most_negative_first)

        print "Gold territory:", [str(pos) for pos in safest_gold_spots]
        print "Silver territory:", [str(pos) for pos in safest_silver_spots]

        def to_string(the_map):
            for piece in the_map.keys():
                print str(piece), "=>"
                for otherpiece in the_map[piece]:
                    print "\t", str(otherpiece), "\t(", the_map[piece][otherpiece], ")"

        print "Distance Map:" 
        to_string(distance_map())
            

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
                    aggro_map[i][j] += float(PIECE_AGGRO[piece.char])/((dist + 1.0) ** 2)
                aggro_map[i][j] += trap_influence(current_pos)
    #Give each piece a mobility
    most_mobile, most_mobility = None, 0
    for piece in pieces:
        row = piece.position.row
        col = piece.position.col
        piece.mobility = 0 if frozen(piece) else explore(piece, row, col, 4) #mobility(piece)
        print piece, piece.mobility
        if piece.mobility >= most_mobility:
            most_mobile = piece
            most_mobility = piece.mobility
    print "Most mobile piece: ", most_mobile

    decide(aggro_map)
    
    # Return the scored board
    return aggro_map

def most_mobile_piece(pieces):
    most_mobility, most_mobile = 0, None
    for piece in pieces:
        if piece.mobility > most_mobility:
            most_mobility = piece.mobility
            most_mobile = piece
    return most_mobile





# def decide(board, golds_turn):
#     from decisiontree import *
#     import questions

#     question = questions.retrieve_for(board, golds_turn)


#     tree = DecisionTree()
#     root = Node(question = question.are_my_rabbits_near_the_goal,   # an open goal spot?
#                 yes = Node(question = question.are_those_rabbits_mobil:qe, 
#                             yes = Node(question = question.can_the_rabbit_reach_the_goal,
#                                         yes = Node(question = question.)



