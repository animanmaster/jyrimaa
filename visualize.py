from javax.swing import *
from javax.swing.filechooser import FileNameExtensionFilter
from javax.imageio import ImageIO
from java.awt import BorderLayout, GridLayout, Color
from java.awt.event import FocusListener, MouseAdapter, MouseEvent
from java.awt.image import BufferedImage
from java.io import File

import sys
import traceback

from gamedb import *

#YAY I GOT RID OF THE AWFULNESS! :D
filechooser = JFileChooser();
pyfilter = FileNameExtensionFilter("Python script", ["py"])
dbfilter = FileNameExtensionFilter("Games Database", ["db"])

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
    return row % 2 and (col % 2 and Color.GREEN or Color.WHITE) or (col % 2 and Color.WHITE or Color.GREEN)

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

    def __init__(self, db = "./games.db", gameid = None, turnid = None, scoringModule = "./scoreState.py"):
        self.frame = JFrame("Scoring Sandbox",
                            defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                            size = (400, 300)
                            )
        self.frame.contentPane = JPanel(BorderLayout(5,5))
        self.gamedb = GameDB(db)
        self.gameid = gameid
        self.turnid = turnid
        self.score = None
        self.colorizer = None
        if gameid and turnid:
            self.board = gamedb.retrieveBoard(gameid, turnid)
        else:
            self.board = Board()
        self.scoringModule = scoringModule
        self.read(scoringModule)
        self.initGui() 
        self.display()

    def label_maker(self, is_board_label):

        def board_label_maker(board_item, i, j, colorizer):
            value = self.scores[i][j]
            label = common_label(its_a_trap(i, j) and "<html><font color='red'><b>X</b></font></html>" or "", 
                                PIECE_IMAGE[board_item and board_item.char or None], i, j, value, colorizer)
            label.toolTipText += " (value = %.2f)" % value
            if board_item:
                #Informative tooltip!
                tooltip = "<html><table>"
                tooltip += "<tr><td>Value:</td><td>%.2f</td></tr>" % value
                tooltip += "<tr><td colspan=2><b>Piece Attributes:</td></tr>"
                for attr, value in board_item.__dict__.iteritems():
                    tooltip += "<tr><td>" + attr.capitalize() + ":</td><td>" + str(value) + "</td></tr>"
                label.toolTipText = tooltip + "</table></html>"

            #Action Popup!
            def make_action(piece, position, direction):
                def actionlistener(e):
                    try:
                        move = Move(piece + position + direction)
                        self.board.apply_move(move)
                        self.reload()
                    except:
                        print sys.exc_info()
                        self.error("Error applying move - " + str(sys.exc_info()))
                return actionlistener

            popup = JPopupMenu()
            pos = make_position(i, j)
            if board_item:
                menu = JMenu("Move")
                if i < 8: menu.add(JMenuItem("Up", actionPerformed=make_action(board_item.char, pos, Direction.NORTH)))
                if j > 0: menu.add(JMenuItem("Left", actionPerformed=make_action(board_item.char, pos, Direction.WEST)))
                if i > 0: menu.add(JMenuItem("Down", actionPerformed=make_action(board_item.char, pos, Direction.SOUTH)))
                if j < 8: menu.add(JMenuItem("Right", actionPerformed=make_action(board_item.char, pos, Direction.EAST)))
                popup.add(menu)
                popup.add(JMenuItem("Clear", actionPerformed=make_action(board_item.char, pos, Direction.DEAD)))
            else:
                menu = JMenu("Place")
                for piece_char in PIECES:
                    menu.add(JMenuItem(piece_char, PIECE_IMAGE[piece_char], actionPerformed=make_action(piece_char, pos, Direction.ALIVE)))
                popup.add(menu)

            class Popupper(MouseAdapter):
                def mouseClicked(m, e):
                    if e.button != MouseEvent.BUTTON1: popup.show(e.component, e.x, e.y)

            label.addMouseListener(Popupper())

            return label

        def number_label_maker(value, i, j, colorizer):
            return common_label("%.2f" % (value), None, i, j, value, colorizer)

        if is_board_label:
            return board_label_maker
        else:
            return number_label_maker

    def parse_code(self, code):
        exec(code)
        self.score = score if "score" in locals() else default_scorer
        self.colorizer = colorizer if "colorizer" in locals() else value_color

    def get_scorer(self, code = None):
        if code: 
            self.parse_code(code)
        scorer = self.score or default_scorer
        return scorer

    def get_colorizer(self):
        return self.colorizer or value_color #self.get_scorer() != default_scorer and value_color or checkerboard

    def read(self, filename):
        try:
            code = open(filename).read()
            self.score = self.get_scorer(code)
            return code
        except:
            print sys.exc_info()
            return None
        

    def save(self, txt, filename):
        f = open(filename, "w")
        f.write(txt)
        f.close()
        
    def initGui(self):
        def reloadButton():
            button = JButton("Reload")
            def reload(evt):
                self.reload()
            button.addActionListener(reload)
            return button

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

            class ML(MouseAdapter):
                def mouseClicked(ml_instance,evt):
                    filechooser.setFileFilter(dbfilter)
                    if(filechooser.showOpenDialog(self.frame) == JFileChooser.APPROVE_OPTION):
                        evt.source.text = filechooser.getSelectedFile().getPath()
                        try:
                            self.gamedb = GameDB(evt.source.text)
                        except:
                            self.error("Error loading database: " + sys.exc_info())
                        self.gameChanger = True

            selector = JPanel()
            selector.add(JLabel("DB:"))
            #selector.add(textfield(self.gamedb.dbfile, dbChange))
            button = JButton("Choose DB")
            button.addMouseListener(ML())
            selector.add(button)
            selector.add(JLabel("Game ID:"))
            selector.add(textfield(self.gameid, idChange))
            selector.add(JLabel("Turn ID:"))
            selector.add(textfield(self.turnid, turnChange))
            selector.add(reloadButton())
            return JScrollPane(selector)

        def make_content_panel():
            self.contentPanel = JPanel(GridLayout(1, 0, 5, 5))
            self.render()
            return JScrollPane(self.contentPanel)

        def make_code_editor():
            panel = JPanel(BorderLayout(2,2))
            self.codeArea = JTextArea()
            self.codeArea.text = self.scoringModule and self.read(self.scoringModule) or ""
            panel.add(JScrollPane(self.codeArea), BorderLayout.CENTER)
            buttonpanel = JPanel(GridLayout(1,0, 2,2))
            button = JButton("Open File")
            def open_file(e):
                filechooser.setFileFilter(pyfilter)
                if(filechooser.showOpenDialog(self.frame) == JFileChooser.APPROVE_OPTION):
                    self.scoringModule = filechooser.getSelectedFile().getPath()
                    self.codeArea.text = self.read(self.scoringModule)
            button.addActionListener(open_file)
            buttonpanel.add(button)
            button = JButton("Save File")
            def save_file(e):
                filechooser.setFileFilter(pyfilter)
                if (filechooser.showSaveDialog(self.frame) == JFileChooser.APPROVE_OPTION):
                    self.scoringModule = filechooser.getSelectedFile().getPath()
                    self.save(self.codeArea.text, self.scoringModule)
            button.addActionListener(save_file)
            buttonpanel.add(button)
            panel.add(buttonpanel, BorderLayout.SOUTH)
            return panel

        self.frame.contentPane.add(make_game_selector(), BorderLayout.NORTH)
        pane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, make_content_panel(), make_code_editor())
        pane.setDividerLocation(self.frame.width/2)
        self.frame.contentPane.add(pane, BorderLayout.CENTER)
        self.frame.contentPane.add(reloadButton(), BorderLayout.SOUTH)

    def render(self):
        self.score, self.colorizer = (self.get_scorer(), self.get_colorizer())
        self.scores = self.score(self.board)
        self.contentPanel.removeAll()
        self.contentPanel.add(make_board_panel(self.board, self.label_maker(True), self.colorizer))
        self.contentPanel.add(make_board_panel(self.scores, self.label_maker(False), self.colorizer))
        self.contentPanel.revalidate()

    def reload(self):
        try:
            if self.gameChanger:
                self.board = self.gamedb.retrieveBoard(self.gameid, self.turnid)
                self.gameChanger = False
            #self.score = self.get_scorer(self.codeArea.text)
            self.parse_code(self.codeArea.text)
            self.render()
        except:
            self.error("An Exception Occurred: " + str(sys.exc_info()))

    def error(self, message):
        print sys.exc_info()
        traceback.print_tb(sys.exc_info()[2])
        JOptionPane.showMessageDialog(self.frame, message, "Error", JOptionPane.ERROR_MESSAGE)


    def display(self):
        self.frame.pack()
        self.frame.visible = True
        self.reload()

if __name__ == "__main__":
    sandbox = ScoringSandbox()
