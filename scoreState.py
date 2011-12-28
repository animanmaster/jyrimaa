from gamedb import *
from javax.swing import BorderFactory, JFrame, JPanel, JLabel
from java.awt import GridLayout, Color


PIECES = ['E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r']
AGGRO  = [ 32,  16,   8,   4,   2,   1, -32, -16,  -8,  -4,  -2,  -1]

PIECE_AGGRO = dict(zip(PIECES, AGGRO))

def distance(position1, position2):
    return abs(position1.row - position2.row) + abs(position1.col - position2.col)

#THOUGHT: Each spot contains values for each piece, taking into account the pieces blocking the way and pieces that could freeze you.
#TODO - Consider trap positions and capture patterns

# Mobility = 0 if frozen or surrounded by pieces that can't be pushed (?).
# Examine the piece's AOI?
# Higher mobility = higher freedom of movement.
def mobility(piece, board):
    pieces = board.pieces
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

    def common_label(display, i, j, value):
        return JLabel(display, None, JLabel.CENTER,
                      border = BorderFactory.createLineBorder(Color.black),
                      toolTipText = make_position(i, j),
                      opaque = True,
                      background = value_color(value))
                    
    def label_maker(board_item, color, i, j):
        value = aggro[i][j]
        return common_label(board_item and str(board_item)[0] or " ", i, j, value)

    frame.contentPane = JPanel(GridLayout(1,0, 10, 10))

    frame.contentPane.add(make_board_panel(board, board_colors, label_maker))

    def label_maker(value, color, i, j):
        return common_label("%.2f" % (value), i, j, value)

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

