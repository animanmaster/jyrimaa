from piece_data import PieceData
import itertools

class GameAcumen:
	def __init__(self):
		self.knowledgebase = {}
		#self.evaluator = evaluator

	def calculate_hashes(self, board_data):
		return [hash(board_data.hash_value(radius + 1)) for radius in range(PieceData.MAX_RADIUS)]

	def calculate_move_value(self, game_data, player):
		wrating, brating, winner = game_data
		# TODO account for the difference between players
		if player == 'w':
			player_rating = wrating
		else:
			player_rating = brating

		multiplier = (winner != player and winner not in ['d', 'u']) and -1 or 1
		return player_rating * multiplier

	def learn(self, board_data, moves, game_data, player):
		# TODO Use an evaluator object to abstract out the multiplier
		# That'll make it easier when it's time to learn win-in-2/killer/definitely-good/bad-moves
		premove_piece_data = board_data.piece_data()
		board_data.apply_moves(moves)
		postmove_piece_data = board_data.piece_data()
		self.knowledgebase.learn(premove_piece_data, postmove_piece_data, self.calculate_move_value(game_data, player))

class Knowledgebase:
	class Node:
		def __init__(self):
			self.learned = LearnedMoves()
			self.next = {}

		def accept(self, hashes, result_hash, value):
			hash_str = hashes.pop(0)
			self.learned.update(hash_str, value/(len(hashes) + 1))
			if len(hashes):
				if hashes[0] in self.next:
					node = self.next[hashes[0]]
				else:
					node = Node()
					self.next[hashes[0]] = node
				node.accept(hashes, result_hash, value)


	def __init__(self):
		self.root = Node()

	def learn(self, before_piece_data, after_piece_data, value):
		before_piece_data, after_piece_data = set(before_piece_data), set(after_piece_data)
		affected = list(before_piece_data - after_piece_data)
		affected.sort() # affected is now a sorted collection of PieceData objects that were affected by this move.
		diff = after_piece_data - before_piece_data
		# result = ''.join((''.join(radius_hashes) for radius_hashes in itertools.izip([piece_data.chunked_full_hash() for piece_data in diff])))
		result = [''.join(radius_hashes) for radius_hashes in itertools.izip((piece_data.chunked_full_hash() for piece_data in diff))] # [all_r1_pd_hashes, all_r2_pd_hashes, etc] in diff
		# result is now an array of radius hashes for the affected piece in the move.
		# By splitting it up by radius, we can do "best partial matches" where the move matches only up to a certain radius.
		# The higher the radius match the more similar these two states were.
		for affected_piece in affected:
			# For each piece that was affected, tie its piece_data hash with the move result hashes.
			self.root.accept(affected_piece.chunked_full_hash(), result, value)

	def collect_options(self, before_piece_data):
		for piece_data in before_piece_data:
			pass # TODO retrieve the moves that may match this piece data from the knowledgebase.

class LearnedMoves:
	def __init__(self):
		self.states = {}
		self.max_moves = None
		self.min_moves = None
		self.dirty = False

	def update(self, state_hash, value):
		if state_hash not in self.states:
			self.states[state_hash] = [float(value), 1]
		else:
			result = self.states[state_hash]
			result[0] += value
			result[1] += 1
		self.dirty = True

	def _recalc_min_and_max(self):
		minimum = maximum = None
		min_moves = max_moves = None
		for state_hash, (value, occurrences) in self.states.iteritems():
			normalized_value = value/occurrences

			if minimum is None or normalized_value < minimum:
				minimum = normalized_value
				min_moves = [state_hash]
			elif normalized_value == minimum:
				min_moves.append(state_hash)

			if maximum is None or normalized_value > maximum:
				maximum = normalized_value
				max_moves = [state_hash]
			elif normalized_value == maximum:
				max_moves.append(state_hash)

		self.min_moves = min_moves
		self.max_moves = max_moves
		self.minimum_value = minimum
		self.maximum_value = maximum
		self.dirty = False

	def maximum_moves(self):
		if self.dirty:
			self._recalc_min_and_max()
		return self.max_moves

	def minimum_moves(self):
		if self.dirty:
			self._recalc_min_and_max()
		return self.min_moves
