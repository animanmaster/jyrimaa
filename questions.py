from databag import DataBag

def retrieve_for(board, golds_turn):

    pieces_on_board = dict([(piece.char, piece) for piece in PIECES])
	data = DataBag()

    def piece_check(piece_chars, check):
        matched_pieces = []
        for char in piece_chars:
            piece = pieces_on_board[char]
            if check(piece): matched_pieces.append(piece)
        return matched_pieces

    def are_rabbits_near_the_goal(mine=True, opponents=False):
        rabbit_proximity = lambda piece: piece.position.row >= 3 if piece.char.isupper() else piece.position.row <= 4
        piecetypes = ['R', 'r']
        if golds_turn:
        	if not mine:
        		piecetypes.remove('R')
        	if not opponents:
        		piecetypes.remove('r')
        else: #silver
        	if not mine:
        		piecetypes.remove('r')
        	if not opponents:
        		piecetypes.remove('R')

        data.rabbits_almost_there = piece_check(piecetypes, rabbit_proximity)
        return lambda **kwargs: len(data.rabbits_almost_there) > 0

    def are_those_rabbits_mobile(**kwargs):
    	mobile_rabbits = []
    	max_mobility, most_mobile = 0, None
    	for rabbit in data.rabbits_almost_there:
    		if rabbit.mobility > 0: mobile_rabbits.append(rabbit)
    		if rabbit.mobility > max_mobility:
    			max_mobility, most_mobile = rabbit.mobility, rabbit
    	data.mobile_rabbits = mobile_rabbits
    	data.most_mobile_rabbit = most_mobile
    	return len(mobile_rabbits) > 0

    
    

	return DataBag(data = data,
				   are_my_rabbits_near_the_goal = are_rabbits_near_the_goal(mine=True, opponents=False),
				   are_their_rabbits_near_the_goal = are_rabbits_near_the_goal(mine=False, opponents=True),
				   are_those_rabbits_mobile = are_those_rabbits_mobile)