
class Piece:
    def __init__(self, char, position):
        self.char = str(char)[0]
        self.position = position

    def friend_of(self, otherpiece):
        return otherpiece and ((self.char.isupper() and otherpiece.char.isupper()) or (self.char.islower() and otherpiece.char.islower()))


    def __str__(self):
        return str(self.char) + str(self.position)

