
class Piece:
    def __init__(self, char, position):
        self.char = str(char)[0]
        self.position = position

    def __str__(self):
        return str(self.char) + str(self.position)

