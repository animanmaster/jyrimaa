from piece_data import PieceData
from move import Move

class BoardData:
	def __init__(self, board): #, player):
		self.board = board
		#self.player = player
		self._reset_cached_values()

	def _reset_cached_values(self):
		self._piece_data = None
		self._chunked = None

	@property
	def piece_data(self):
		if self._piece_data is None:
			self._piece_data = sorted((self.board.calculate_piece_data(piece) for piece in self.board.pieces))
		return self._piece_data

	def chunked_hashes(self):
		'''
		Return the full hash chunked by radius.

		>>> bd.chunked_hashes()
		['002001102001103001', '020100020100020100', '103121103121103121', '0a00210a00210a0021', '011100011100011100', '100000100000100000', '100001100001100001', '200000200000200000', '000800000800000800', '000000000000000000', '100000100000100000', '500400500400500400', '000000000000000000', '001000001000001000']
		'''
		if self._chunked is None:
			self._chunked = [''.join(radius_group) for radius_group in zip(*[pd.chunked_full_hash() for pd in self.piece_data])]
		return self._chunked

	def hash_value(self, radius=None):
		'''
		Return the hash value of this board by concatenating the sorted piece data hashes.
		Given a radius, the hash will be a concatenation of all the piece data hashes of the given radius.

		>>> bd.hash_value()
		'0020011020011030010201000201000201001031211031211031210a00210a00210a0021011100011100011100100000100000100000100001100001100001200000200000200000000800000800000800000000000000000000100000100000100000500400500400500400000000000000000000001000001000001000'
		>>> bd.hash_value(4)
		'0020011020011030010201000201000201001031211031211031210a00210a00210a0021'
		'''
		hashes = self.chunked_hashes()
		return ''.join(radius and hashes[:radius] or hashes)

	def apply_moves(self, moves):
		'''
		Apply the given moves to the board.
		'''
		for move in moves:
			if len(move) > 0:
				self.board.apply_move(Move(move))
		self._reset_cached_values()



if __name__ == "__main__":
    import doctest
    bd = BoardData(None)
    pd1 = PieceData()
    pd2 = PieceData()
    pd3 = PieceData()
    pd1.hashed = '0020010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
    pd2.hashed = '1020010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
    pd3.hashed = '1030010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
    bd._piece_data = [pd1, pd2, pd3]
    doctest.testmod(extraglobs={'bd': bd})
