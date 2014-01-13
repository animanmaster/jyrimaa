from piece_data import PieceData

class BoardData:
	def __init__(self, board, player):
		self.board = board
		self.player = player
		self._piece_data = None

	@property
	def piece_data(self):
		if self._piece_data is None:
			self._piece_data = sorted((board.calculate_piece_data(piece) for piece in board.pieces))
		return self._piece_data

	def hash_value(self, radius=None):
		'''
		Return the hash value of this board by concatenating the sorted piece data hashes.
		Given a radius, the hash will be a concatenation of all the piece data hashes of the given radius.

		>>> bd.hash_value()
		'0020010201001031210a00210111001000001000012000000008000000001000005004000000000010001020010201001031210a00210111001000001000012000000008000000001000005004000000000010001030010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
		>>> bd.hash_value(4)
		'0020010201001031210a00211020010201001031210a00211030010201001031210a0021'
		'''
		return ''.join((pd.get_hash(radius) for pd in self.piece_data))

	def apply_moves(self, moves):
		'''
		Apply the given moves to the board.
		'''
		for move in moves:
			self.board.apply_move(Move(move))
		self._piece_data = None



if __name__ == "__main__":
    import doctest
    bd = BoardData(None, None)
    pd1 = PieceData()
    pd2 = PieceData()
    pd3 = PieceData()
    pd1.hashed = '0020010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
    pd2.hashed = '1020010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
    pd3.hashed = '1030010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
    bd._piece_data = [pd1, pd2, pd3]
    doctest.testmod(extraglobs={'bd': bd})
