from gamedb import *

b = Board()
print b

b.place("r", "A1")
b.place("E", "A2")

print b

move = Move("ra1e")
b.apply_move(move)
print b

b.undo_move(move)
print b

db = GameDB("./games.db")
board = db.retrieveBoard(4, "26b")
print board

# for piece in board.pieces:
#     print piece

potentials = {
	'r' :  1, 'c' :  2, 'd' :  3, 'h' :  4, 'm' :  5, 'e' :  6,
	'R' :  1, 'C' :  2, 'D' :  3, 'H' :  4, 'M' :  5, 'E' :  6
}

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

print "Gold Potential:"
for row in gold_potential:
	print ''.join(["{0}\t".format(value) for value in row])

print "Silver Potential:"
for row in silver_potential:
	print ''.join(["{0}\t".format(value) for value in row])


