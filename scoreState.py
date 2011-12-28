from gamedb import *
from javax.swing import BorderFactory, JFrame, JPanel, JLabel, ImageIcon
from javax.imageio import ImageIO
from java.awt import GridLayout, Color

IMAGE_DIR = './images/orig/'

PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r')
IMAGES = ('GoldElephant.gif', 'GoldCamel.gif', 'GoldHorse.gif', 'GoldDog.gif', 'GoldCat.gif', 'GoldRabbit.gif', \
          'SilverElephant.gif', 'SilverCamel.gif', 'SilverHorse.gif', 'SilverDog.gif', 'SilverCat.gif', 'SilverRabbit.gif')
AGGRO  = ( 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1)

TRAPS = ((2,2), (2,5), (5,2), (5,5))

PIECE_AGGRO = dict(zip(PIECES, AGGRO))
PIECE_IMAGE = dict(zip(PIECES, IMAGES))

for piece, image_file in PIECE_IMAGE.iteritems():
    PIECE_IMAGE[piece] = ImageIcon(IMAGE_DIR + image_file)

PIECE_IMAGE[None] = None

def its_a_trap(row, col):
    return ((row == 2 or row == 5) and (col == 2 or col == 5))

def distance(position1, position2):
    return abs(position1.row - position2.row) + abs(position1.col - position2.col)

def find_piece(board, row, col):
    return (0 <= row <= 7 and 0 <= col <= 7 and board[row][col]) or None 

def friend(piece, otherpiece):
    return otherpiece and ((piece.char.isupper() and otherpiece.char.isupper()) or (piece.char.islower() and otherpiece.char.islower()))

def surrounding_pieces(board, row, col):
    return find_piece(board, row + 1, col), find_piece(board, row - 1, col), find_piece(board, row, col - 1), find_piece(board, row, col + 1)

def forever_alone(piece, board):
    row, col = piece.position.row, piece.position.col
    above, below, left, right = surrounding_pieces(board, row, col)
    return not (friend(piece, above) or friend(piece, below) or friend(piece, left) or friend(piece, right)) #no one around you? Forever alone.

def frozen(piece, board):
    row, col = piece.position.row, piece.position.col
    myaggro = abs(PIECE_AGGRO[piece.char])
    no_friends = forever_alone(piece, board)
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
#TODO - Consider trap positions and capture patterns
#ANOTHER THOUGHT (RELATED TO THE TODO): The trap exudes the sum(half the power of the piece it's next to?)

# Mobility = 0 if frozen or surrounded by pieces that can't be pushed (?).
# Examine the piece's AOI?
# Higher mobility = higher freedom of movement.
def mobility(piece, board):
    pieces = board.pieces
    if frozen(piece, board):
        return 0
    
    for board_piece, position in pieces.iteritems():
        if board_piece != piece:
            pass

            

def score(board):
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
                    aggro_map[i][j] += float(PIECE_AGGRO[piece.char])/(dist + 1.0)
    return aggro_map


def make_board_panel(board, board_colors, content_maker):
    panel = JPanel(GridLayout(8, 8))
    color_index = 0
    for i in range(8, 0, -1):
        for j in range(8):
            panel.add(content_maker(board[i - 1][j], board_colors[color_index], i-1, j))
            color_index = (color_index + 1) % len(board_colors)
        color_index = (color_index + 1) % len(board_colors) #slight hack to give us a checkerboard!
    return panel


def show_colored(board, aggro):

    frame = JFrame("Board Visualization",
                   defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                   size = (400, 300)
                   )

    board_colors = (Color.white, Color.black)
#    board_colors = (Color(Color.white.red, Color.white.green, Color.white.blue, 128),
#                    Color(Color.black.red, Color.black.green, Color.black.blue, 128))
    
    def value_color(value):
        #scaling it by 4 so that the colors are more discernible
        return Color((value > 0) and max(0, int(255 - value * 4)) or 255, 255, (value < 0) and max(0, int(255 + value * 4)) or 255)

    def common_label(display, image_file, i, j, value):
        return JLabel(display, image_file or None, JLabel.CENTER,
                      border = BorderFactory.createLineBorder(Color.black),
                      toolTipText = make_position(i, j),
                      opaque = True,
                      background = value_color(value))
                    
    def label_maker(board_item, color, i, j):
        value = aggro[i][j]
        return common_label(board_item and "" or (its_a_trap(i, j) and "<html><font color='red'><b>X</b></font></html>" or ""), PIECE_IMAGE[board_item and board_item.char or None], i, j, value)

    frame.contentPane = JPanel(GridLayout(1,0, 10, 10))

    frame.contentPane.add(make_board_panel(board, board_colors, label_maker))

    def label_maker(value, color, i, j):
        return common_label("%.2f" % (value), None, i, j, value)

    frame.contentPane.add(make_board_panel(aggro, board_colors, label_maker))

    frame.visible = True



db = GameDB("games.db")
board = db.retrieveBoard(4, "26b")
print board

aggro = score(board)
aggro_str = ""
for row in aggro:
    for val in row:
        aggro_str += ("%.2f\t" % (val)).rjust(6)
    aggro_str += "\n"

show_colored(board, aggro)

print aggro_str

for piece in board.pieces:
    if frozen(piece, board):
        print piece, "is frozen."

