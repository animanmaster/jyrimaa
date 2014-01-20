from piece_data import PieceData
import itertools

class GameAcumen:
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
				elif normalized_value == minimum
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

			
	def __init__(self):
		self.knowledgebase = {}
		#self.evaluator = evaluator

	def calculate_hashes(self, board_data):
		return [board.hash_value(radius + 1) for radius in range(PieceData.MAX_RADIUS)]

	def calculate_move_value(self, game_data, player):
		wrating, brating, winner = game_data
		# TODO account for the difference between players
		if player == 'w':
			player_rating = wrating
		else:
			player_rating = brating

		multiplier = (winner != player and winner not in ['d', 'u']) and -1 or 1
		return player_rating * multiplier

	def save_move(self, before_hashes, after_hashes, move_value):
		for before_hash, after_hash in itertools.izip(before_hashes, after_hashes:
			if before_hash not in self.knowledgebase:
				self.knowledgebase[before_hash] = GameAcumen.LearnedMoves()
			self.knowledgebase[before_hash].update(after_hash, move_value)

	def learn(self, board_data, moves, game_data, player):
		# TODO Use an evaluator object to abstract out the multiplier
		# That'll make it easier when it's time to learn win-in-2/killer/definitely-good/bad-moves
		premove_hashes = self.calculate_hashes(board_data)
		board_data.apply_moves(moves)
		postmove_hashes = calculate_hashes(board_data)
		self.save_move(premove_hashes, postmove_hashes, self.calculate_move_value(game_data, player))
