from javax.swing import BorderFactory, JFrame, JPanel, JLabel, ImageIcon, JScrollPane, JTextArea, JTextField, JButton, JSplitPane
from javax.imageio import ImageIO
from java.awt import BorderLayout, GridLayout, Color, GridBagLayout
from java.awt.event import FocusListener, MouseAdapter
from java.awt.image import BufferedImage
from java.io import File

# :/ I don't really like this here.
import scoreState
from scoreState import *    # I MADE IT WORSE! THIS IMPLICITLY IMPORTS ALL THE OTHER STUFF! I'M A HORRIBLE PERSON! D:
from game_examiner import *



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

def make_board_panel(board, content_maker, colorizer):
    panel = JPanel(GridLayout(8, 8))
    for i in range(8, 0, -1):
        for j in range(8):
            panel.add(content_maker(board[i - 1][j], i-1, j, colorizer))
    return panel

def bounded(value):
    return int(min(255, max(0, value)))

def value_color(value, i = None, j = None):
    #scaling it by 4 so that the colors are more discernible
    scale_factor = 4
    value *= scale_factor
    default = 0
    return Color((value > 0) and bounded(255 - value) or default,
                  default,
                  (value < 0) and bounded(255 + value) or default)

                    
def common_label(display, image_file, i, j, value, colorizer):
    return JLabel(display, image_file or None, JLabel.CENTER,
                  border = BorderFactory.createLineBorder(Color.black),
                  toolTipText = make_position(i, j),
                  opaque = True,
                  background = colorizer(value, i, j))

# TODO: A class that takes a board and scoring function, displays the colored board and aggro and source and allows the source to be changed and re-evaluated dynamically. To be extra cool, be able to save the source, change game and move id, change board state manually, reset, etc.

def eight_by_eight_of(things):
    return [ [things] * 8 for i in range(8) ]

def checkerboard(_, row, col):
    return row % 2 and (col % 2 and Color.BLACK or Color.WHITE) or (col % 2 and Color.WHITE or Color.BLACK)

def default_scorer(board):
    return eight_by_eight_of(0)

def textfield(text = "", actionListener = None):
    txt = JTextField(text, 15)
    class Focuser(FocusListener):
        def focusGained(self,e):
            pass
        def focusLost(self,e):
            if actionListener: actionListener(e)
    txt.addFocusListener(Focuser())
#    if actionListener: txt.addActionListener(actionListener)
    return txt

class BoardViewer(JPanel):

  def __init__(self, db, game_id=None, turn_id=None, board=None):
    self.gamedb = db
    self.game_id = game_id
    self.turn_id = turn_id
    self.board = board
    JPanel.__init__(self, BorderLayout(5,5))
    self.initGui()

  def initGui(self):
    self.gameChanger = False
    self.board_container = JPanel()
    self.setBorder(BorderFactory.createLineBorder(Color.black))
    self.add(self.make_game_selector(), BorderLayout.NORTH)
    self.add(self.board_container, BorderLayout.CENTER)
    self.add(self.make_action_panel(), BorderLayout.SOUTH)
    # self.glass = self.glassPane
    # self.glass.setLayout(GridBagLayout())
    # self.glass.add(JLabel("Loading..."))

  def make_game_selector(self):
    def idChange(evt):
        if evt.source.text: 
            self.game_id = evt.source.text
            self.gameChanger = True
    def turnChange(evt):
        if evt.source.text: 
            self.turn_id = evt.source.text
            self.gameChanger = True

    selector = JPanel()
    selector.add(JLabel("Game ID:"))
    selector.add(textfield(self.game_id, idChange))
    selector.add(JLabel("Turn ID:"))
    selector.add(textfield(self.turn_id, turnChange))
    return selector

  def board_spot(self, i, j):
    board_item = self.board[i][j]
    label = common_label(its_a_trap(i, j) and "<html><font color='red'><b>X</b></font></html>" or "", 
                        PIECE_IMAGE[board_item and board_item.char or None], i, j, 0, lambda *args: Color.WHITE)
    if board_item:
        tooltip = "<html><table>"
        for attr, value in board_item.__dict__.iteritems():
            tooltip += "<tr><td>" + attr.capitalize() + ":</td><td>" + str(value) + "</td></tr>"
    return label

  def make_board_panel(self):
    panel = JPanel(GridLayout(8, 8))

    def piece_data_setter(row, col):
      if self.board and self.board[row][col]:
        def show_piece_data():
          self.textarea.setText(
            ('<html>Moves: %s<br />' % self.board.moves) + 
            str(calculate_piece_data(self.board, self.board[row][col]))
          )
        return show_piece_data
      else:
        return lambda *a: None

    self.currently_highlighted = None
    def unhighlight(thing):
      thing.setBackground(Color.WHITE)
    def highlight(thing):
      thing.setBackground(Color.YELLOW)

    def click_spot_listener(i, j):
      set_piece_data = piece_data_setter(i, j)
      class ML(MouseAdapter):
        def mousePressed(_, evt):
          if self.currently_highlighted == evt.source:
            unhighlight(evt.source)
            self.textarea.setText('')
            self.currently_highlighted = None
          else:
            if self.currently_highlighted: unhighlight(self.currently_highlighted)
            highlight(evt.source)
            self.currently_highlighted = evt.source
            set_piece_data()
      return ML()

    if self.board:
      for i in range(8, 0, -1):
        for j in range(8):
          spot = self.board_spot(i - 1, j)
          panel.add(spot)
          spot.addMouseListener(click_spot_listener(i - 1, j))
    return panel


  def make_action_panel(self):
    panel = JPanel()
    reload_button = JButton("Reload")
    remove_button = JButton("Remove")
    def reload_action(evt):
      self.reload()
    def remove_action(evt):
      self.remove()
    reload_button.addActionListener(reload_action)
    remove_button.addActionListener(remove_action)
    panel.add(reload_button)
    panel.add(remove_button)
    self.textarea = JLabel()
    container = JPanel(BorderLayout())
    container.add(panel, BorderLayout.NORTH)
    container.add(self.textarea, BorderLayout.CENTER)
    return container

  def remove(self):
    parent = self.parent
    parent.remove(self)
    parent.revalidate()

  def reload(self):
    if self.gameChanger:
      self.board = self.gamedb.retrieveBoard(self.game_id, self.turn_id)
      self.board_container.removeAll()
      self.board_container.add(self.make_board_panel())
    self.revalidate()



class MultiGameViewer:
    def __init__(self, db = "./games.db", scoringModule = scoreState):
        self.gamedb = GameDB(db)
        self.scoringModule = scoringModule
        self.score = scoringModule and scoringModule.score or default_scorer
        self.boards = []
        self.initGui()

    def new_add_game_panel(self):
      panel = JPanel(GridBagLayout(), border = BorderFactory.createLineBorder(Color.black))
      def add_game(evt):
        panel.removeAll()
        new_viewer = BoardViewer(self.gamedb)
        # new_viewer.index = len(self.boards)
        panel.add(new_viewer)
        self.gameStrip.add(self.new_add_game_panel())
        self.gameStrip.revalidate()
        # self.boards.append(new_viewer)
      add_button = JButton("+ Add Game")
      add_button.addActionListener(add_game)
      panel.add(add_button)
      return panel
        
    def initGui(self):
        self.frame = JFrame("Multi-Game Viewer",
                            defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                            size = (400, 300)
                            )
        self.frame.contentPane = JPanel(BorderLayout(5,5))
        self.gameStrip = JPanel()#GridLayout(1,0,2,2))
        self.frame.contentPane.add(JScrollPane(self.gameStrip))
        self.gameStrip.add(self.new_add_game_panel())

    def display(self):
        self.frame.pack()
        self.frame.visible = True
        self.frame.repaint()

if __name__ == "__main__":
    viewer = MultiGameViewer()
    viewer.display()
