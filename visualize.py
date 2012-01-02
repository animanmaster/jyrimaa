from javax.swing import BorderFactory, JFrame, JPanel, JLabel, ImageIcon
from javax.imageio import ImageIO
from java.awt import BorderLayout, GridLayout, Color
from java.awt.image import BufferedImage
from java.io import File

# :/ I don't really like this here.
from board import its_a_trap
from position import make_position


IMAGE_DIR = './images/orig/'
PIECES = ('E', 'M', 'H', 'D', 'C', 'R', 'e', 'm', 'h', 'd', 'c', 'r')
IMAGES = ('GoldElephant.gif', 'GoldCamel.gif', 'GoldHorse.gif', 'GoldDog.gif', 'GoldCat.gif', 'GoldRabbit.gif', \
          'SilverElephant.gif', 'SilverCamel.gif', 'SilverHorse.gif', 'SilverDog.gif', 'SilverCat.gif', 'SilverRabbit.gif')
PIECE_IMAGE = dict(zip(PIECES, IMAGES))

for piece, image_file in PIECE_IMAGE.iteritems():
    image = ImageIO.read(File(IMAGE_DIR + image_file))
    resized_image = BufferedImage(50, 50, BufferedImage.TYPE_INT_ARGB)
    g = resized_image.createGraphics()
    g.drawImage(image, 0, 0, 50, 50, 0, 0, image.width, image.height, None)
    g.dispose()
    PIECE_IMAGE[piece] = ImageIcon(resized_image)
PIECE_IMAGE[None] = None



#TODO - fix this mess! show_colored should be moved out of here, I think.
# This module should only have helpers like make_board_panel and maybe some
# classes for different view thingies.

def make_board_panel(board, content_maker):
    panel = JPanel(GridLayout(8, 8))
    for i in range(8, 0, -1):
        for j in range(8):
            
            panel.add(content_maker(board[i - 1][j], i-1, j))
    return panel

def bounded(value):
    return int(min(255, max(0, value)))

def value_color(value):
    #scaling it by 4 so that the colors are more discernible
    scale_factor = 4
    value *= scale_factor
    default = 255
    return Color((value > 0) and bounded(255 - value) or default,
                  default,
                  (value < 0) and bounded(255 + value) or default)

                    
def common_label(display, image_file, i, j, value):
    return JLabel(display, image_file or None, JLabel.CENTER,
                  border = BorderFactory.createLineBorder(Color.black),
                  toolTipText = make_position(i, j),
                  opaque = True,
                  background = value_color(value))

def show_colored(board, aggro):

    frame = JFrame("Board Visualization",
                   defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                   size = (400, 300)
                   )

    def label_maker(board_item, i, j):
        value = aggro[i][j]
        return common_label(board_item and "" or (its_a_trap(i, j) and "<html><font color='red'><b>X</b></font></html>" or ""), 
                            PIECE_IMAGE[board_item and board_item.char or None], i, j, value)

    frame.contentPane = JPanel(GridLayout(1,0, 10, 10))
    frame.contentPane.add(make_board_panel(board, label_maker))

    def label_maker(value, i, j):
        return common_label("%.2f" % (value), None, i, j, value)

    frame.contentPane.add(make_board_panel(aggro, label_maker))

    frame.pack()
    frame.visible = True



# TODO: A class that takes a board and scoring function, displays the colored board and aggro and source and allows the source to be changed and re-evaluated dynamically. To be extra cool, be able to save the source, change game and move id, change board state manually, reset, etc.

def eight_by_eight_of(things):
    return [ [things] * 8 for i in range(8) ]

def checkerboard(_, row, col):
    return row % 2 and (col % 2 and Color.BLACK or Color.WHITE) or (col % 2 and Color.WHITE or Color.BLACK)

def default_scorer(board):
    return eight_by_eight_of(0)

class ScoringSandbox:
    DEFAULT_BOARD = eight_by_eight_of(None)

    def __init__(self):
        self.frame = JFrame("Scoring Sandbox",
                            defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                            size = (400, 300)
                            )
        self.panel = JPanel(BorderLayout(5,5))
        self.frame.contentPane = self.panel
        self.board = DEFAULT_BOARD
        self.display()

    def display(self, board=None, scorer=default_scorer, colorizer=checkerboard):
        board = board or self.board
        scored = scorer(board)

        



