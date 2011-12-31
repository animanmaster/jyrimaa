from javax.swing import BorderFactory, JFrame, JPanel, JLabel, ImageIcon
from javax.imageio import ImageIO
from java.awt import GridLayout, Color

from board import its_a_trap
from position import make_position


IMAGE_DIR = './images/orig/'

PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r')
IMAGES = ('GoldElephant.gif', 'GoldCamel.gif', 'GoldHorse.gif', 'GoldDog.gif', 'GoldCat.gif', 'GoldRabbit.gif', \
          'SilverElephant.gif', 'SilverCamel.gif', 'SilverHorse.gif', 'SilverDog.gif', 'SilverCat.gif', 'SilverRabbit.gif')
PIECE_IMAGE = dict(zip(PIECES, IMAGES))

for piece, image_file in PIECE_IMAGE.iteritems():
    PIECE_IMAGE[piece] = ImageIcon(IMAGE_DIR + image_file)
PIECE_IMAGE[None] = None


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


