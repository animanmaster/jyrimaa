from gamedb import *

def aggro_colorizer(value, i = None, j = None):
    #scaling it by 4 so that the colors are more discernible
    scale_factor = 4
    value *= scale_factor
    default = 0
    return Color((value > 0) and bounded(255 - value) or default,
                  default,
                  (value < 0) and bounded(255 + value) or default)

def potential_colorizer(value, i=None, j=None):
    return Color(255 - (value * 30), 255, 255)

colorizer = potential_colorizer


def score(board, filter_attr=None):
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
            
    def get_aggro_map():
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
        return aggro_map

    potentials = {
        'r' :  1, 'c' :  3, 'd' :  5, 'h' :  6, 'm' :  8, 'e' :  10,
        'R' :  1, 'C' :  3, 'D' :  5, 'H' :  6, 'M' :  8, 'E' :  10
    }

    def get_potentials():

        gold_potential = [[0] * 8 for i in range(8)]
        silver_potential = [[0] * 8 for i in range(8)]
        row, col = (0, 0)
        spot_potentials = None

        def assign_surrounding_potentials(potential, row, col, surrounding_value):
            if (row > 0): potential[row - 1][col] = max(potential[row - 1][col], surrounding_value)
            if (row < 7): potential[row + 1][col] = max(potential[row + 1][col], surrounding_value)
            if (col > 0): potential[row][col - 1] = max(potential[row][col - 1], surrounding_value)
            if (col < 7): potential[row][col + 1] = max(potential[row][col + 1], surrounding_value)

        def assign_potentials(piece, potential):
            row, col = piece.position.row, piece.position.col
            value = potential[row][col]
            potential[row][col] = max(value, potentials[piece.char])
            surrounding_value =  potential[row][col] - 1
            assign_surrounding_potentials(potential, row, col, surrounding_value)


        for piece in board.pieces:
            if piece.char.isupper():
                assign_potentials(piece, gold_potential)
            else:
                assign_potentials(piece, silver_potential)

        # print "Gold Potential:"
        # for row in gold_potential:
        #     print ''.join(["{0}\t".format(value) for value in row])

        # print "Silver Potential:"
        # for row in silver_potential:
        #     print ''.join(["{0}\t".format(value) for value in row])
        return gold_potential, silver_potential

    def calc_mobilities():
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

    def displacements(gold_potential, silver_potential):
        datplaces = [[{} for i in range(8)] for j in range(8)]

        class Movement:
            def __init__(self, previous, next):
                self.previous = previous
                self.next = next

            def get_possible_moves(self):
                # Return a generator that will allow us to iterate over the possible moves that can make up this movement.
                pass


        def apply_direction(row, col, direction):
            offset = Direction.OFFSET[direction]
            return row + offset[0], col + offset[1]

        # TODO: Push/pulls
        def move_about(piece, gold_potential, silver_potential):
            row, col = piece.position.row, piece.position.col
            if piece.char not in datplaces[row][col]:
                datplaces[row][col][piece.char] = []
            valid_position = lambda r, c: 0 <= r < 8 and 0 <= c < 8

            # Given: 
            #   piece to explore with, 
            #   the current exploration row & col, 
            #   the number of resources left before moving, 
            #   string of moves to get to this spot,
            #   the direction we moved previously to get here (default of None means this is the first iteration)
            # Algorithm:
            #   If a piece exists at this spot, have we explored its displacements yet?
            #       If so, see if it will move out of the way peacibly and within the resources left. 
            #           If so, move it over, append the movements to moves, place yourself there and decrease resources_left to account for the movements appropriately.
            #           Otherwise, 
            #               Can I push it out of the way with the resources I have left? [Note not mentioning pull, since there's no way you can pull a piece and take its spot in one turn]
            #                   If so, do it like above.
            #               Can someone else push/pull it out of the way? 
            #                   [Note, this means we either need to branch out from the target square and find push/pullers or save state and come back when we've calculated it. I'd prefer the latter]
            #                   If so, do it!
            #               Otherwise, I can't get to that spot. :( (sadface)
            #   Otherwise (no piece at this spot),
            #       Do it!
            #   Explore n,e,w,s
                
            if piece.char == 'R':
                directions = [Direction.NORTH, Direction.WEST, Direction.EAST]
            elif piece.char == 'r':
                directions = [Direction.WEST, Direction.SOUTH, Direction.EAST]
            else:
                directions = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]

            # piece.displacements = 0
            piece.displacements = {(piece.position.row, piece.position.col) => [Movement(None, None)]}
            piece.revisit = []
            def can_move_to(piece, row, col):
                piece.displacements |= ((1 << (7 - 8 * row))  << (7 - col))

            def frozen(piece, row, col):
                gold_p, silver_p = gold_potential[row][col], silver_potential[row][col]
                friend_potential, enemy_potential = (piece.char.islower() and (silver_p, gold_p) or (gold_p, silver_p))
                # Frozen if enemy potential is greater than my potential and there are no friendly pieces nearby.
                return (enemy_potential > potentials[piece.char]) and not friend_potential

            def come_back_to(*args):
                piece.revisit.append( args )
                revisit[piece.char].add(piece)

            def add_displacement(piece, row, col, previous_moves, this_move):
                if (row, col) not in piece.displacements:
                    piece.displacements = []
                    revisits.add(piece)
                piece.displacements[(row,col)].append(Movement(previous_moves, this_move))

            def dead(piece, row, col):
                is_trap = Position.is_this_a_trap(row, col)
                potential = (piece.char.islower() and silver_potential[row][col] or gold_potential[row][col])
                # dead if this is a trap and there are no friends nearby (no friendly potential)
                return is_trap and not potential

            # AWESOME: Remember all previous explorations to save time in the future! "Taint" pieces 4 away from moved pieces
            def explore_paths(piece, row, col, resources_left, moves, direction_moved, from_row = None, from_col = None):
                mobility = 0
                initial = False if (from_row and from_col) else True

                if valid_position(row, col):
                    # Append the move to this spot to our string of moves.
                    if not initial:
                        offset = Direction.OFFSET[direction_moved]
                        from_row, from_col = row - offset[0], col - offset[1]
                        step = Move("{0}{1}{2}".format(piece.char, make_position(from_row, from_col), direction_moved))
                else:
                    return mobility

                if resources_left:
                    # We still have resources we can use to move.
                    # Is there a piece at this spot? (besides myself, silly)
                    # Am I frozen at this spot?
                    if frozen(piece, row, col):
                        come_back_to(piece, row, col, resources_left, moves, move, direction_moved, 'frozen') # when we come back, prefer moves that are favorable
                        return mobility
                    if dead(piece, row, col):
                        # TODO Also add "saving" moves before moving to this spot.
                        # resources -= 1
                        # step += "{0}{1}{2}".format(piece.char, make_position(row, col), Direction.DEAD)
                        return mobility + 1

                    existing_piece = board.find_piece(row, col)
                    if initial or not existing_piece or existing_piece.displacements:
                        # If there is no piece here, then I can move easily.
                        if not existing_piece:
                            add_displacement(piece, moves, step)
                        elif existing_piece.displacements:
                            add_displacement(piece, Movement(moves, existing_piece.displacements), step)

                        resources_left -= 1 # Next movement will have one less resource
                        mobility += 1 # Since we've determined I can actually move here, this counts toward my mobility.

                        to_row, to_col = 0, 0
                        # TODO exclude the reverse of direction_moved so we don't have a back-and-forth movement?

                        for direction in directions:
                            to_row, to_col = apply_direction(row,col,direction)
                            mobility += explore_paths(piece, to_row, to_col, resources_left, moves, direction)
                    else:
                        come_back_to(piece, row, col, resources_left, moves, move, direction_moved, is_frozen) # prefer favorable moves

                return mobility

        def revisiting():
            pass


        for piece in pieces:
            move_about(piece)

# ACTUAL SCORING HAPPENS HERE:
    
    aggro_map = get_aggro_map()

    #decide(aggro_map)
    
    gold_potential, silver_potential = get_potentials()
    # potential = [[0] * 8 for i in range(8)]
    # for i in range(8):
    #     for j in range(8):
    #         potential[i][j] = (gold_potential[i][j], silver_potential[i][j])

    # Return the scored board
    #return aggro_map
    return silver_potential

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



