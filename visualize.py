from javax.swing import BorderFactory, JFrame, JPanel, JLabel, ImageIcon, JScrollPane, JTextArea, JTextField, JButton, JSplitPane
from javax.imageio import ImageIO
from java.awt import BorderLayout, GridLayout, Color
from java.awt.event import FocusListener
from java.awt.image import BufferedImage
from java.io import File

# :/ I don't really like this here.
import scoreState
from scoreState import *    # I MADE IT WORSE! THIS IMPLICITLY IMPORTS ALL THE OTHER STUFF! I'M A HORRIBLE PERSON! D:


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

class ScoringSandbox:

    def __init__(self, db = "./games.db", gameid = None, turnid = None, scoringModule = scoreState):
        self.frame = JFrame("Scoring Sandbox",
                            defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                            size = (400, 300)
                            )
        self.frame.contentPane = JPanel(BorderLayout(5,5))
        self.gamedb = GameDB(db)
        self.gameid = gameid
        self.turnid = turnid
        if gameid and turnid:
            self.board = gamedb.retrieveBoard(gameid, turnid)
        else:
            self.board = Board()
        self.scoringModule = scoringModule
        self.score = scoringModule and scoringModule.score or default_scorer
        self.initGui()
        self.display()

    def label_maker(self, is_board_label):
        def board_label_maker(board_item, i, j, colorizer):
            value = self.scores[i][j]
            label = common_label(its_a_trap(i, j) and "<html><font color='red'><b>X</b></font></html>" or "", 
                                PIECE_IMAGE[board_item and board_item.char or None], i, j, value, colorizer)
            if board_item:
                tooltip = "<html><table>"
                for attr, value in board_item.__dict__.iteritems():
                    tooltip += "<tr><td>" + attr.capitalize() + ":</td><td>" + str(value) + "</td></tr>"
                label.toolTipText = tooltip + "</table></html>"
            return label

        def number_label_maker(value, i, j, colorizer):
            return common_label("%.2f" % (value), None, i, j, value, colorizer)

        if is_board_label:
            return board_label_maker
        else:
            return number_label_maker

        
    def initGui(self):
        def make_game_selector():
            self.gameChanger = False
            def dbChange(evt):
                if evt.source.text: 
                    self.gamedb = GameDB(evt.source.text)
                    self.gameChanger = True
            def idChange(evt):
                if evt.source.text: 
                    self.gameid = evt.source.text
                    self.gameChanger = True
            def turnChange(evt):
                if evt.source.text: 
                    self.turnid = evt.source.text
                    self.gameChanger = True

            selector = JPanel()
            selector.add(JLabel("DB:"))
            selector.add(textfield(self.gamedb.dbfile, dbChange))
            selector.add(JLabel("Game ID:"))
            selector.add(textfield(self.gameid, idChange))
            selector.add(JLabel("Turn ID:"))
            selector.add(textfield(self.turnid, turnChange))
            return JScrollPane(selector)

        def make_content_panel():
            self.contentPanel = JPanel(GridLayout(1, 0, 5, 5))
            self.render()
            return JScrollPane(self.contentPanel)

        def save(self, txt, filename):
            pass
            
        def make_code_editor():
            import inspect
            panel = JPanel(BorderLayout(2,2))
            self.codeArea = JTextArea()
            self.codeArea.text = self.scoringModule and inspect.getsource(self.scoringModule) or ""
            panel.add(JScrollPane(self.codeArea), BorderLayout.CENTER)
            return panel

        self.frame.contentPane.add(make_game_selector(), BorderLayout.NORTH)
#        self.frame.contentPane.add(make_content_panel(), BorderLayout.WEST)
#        self.frame.contentPane.add(make_code_editor(),   BorderLayout.CENTER)
        pane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, make_content_panel(), make_code_editor())
        pane.setDividerLocation(self.frame.width/2)
        self.frame.contentPane.add(pane)
        reloadButton = JButton("Reload")
        def reload(evt):
            self.reload()
        reloadButton.addActionListener(reload)
        self.frame.contentPane.add(reloadButton, BorderLayout.SOUTH)

    def render(self):
        self.scorer, self.colorizer = self.score and (self.score, value_color) or (default_scorer, checkerboard)
        self.scores = self.scorer(self.board)
        self.contentPanel.removeAll()
        self.contentPanel.add(make_board_panel(self.board, self.label_maker(True), self.colorizer))
        self.contentPanel.add(make_board_panel(self.scores, self.label_maker(False), self.colorizer))
        self.contentPanel.revalidate()

    def reload(self):
        if self.gameChanger:
            self.board = self.gamedb.retrieveBoard(self.gameid, self.turnid)
            self.scores = self.score(self.board)
            self.gameChanger = False
        exec(self.codeArea.text)
        self.score = score
        self.render()

    def display(self):
        self.frame.pack()
        self.frame.visible = True
        self.reload()

if __name__ == "__main__":
    sandbox = ScoringSandbox()
