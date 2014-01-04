
class TurnData:
    def __init__(self, identifier):
        self.identifier = identifier
        self.moves = {}

    def update(self, before_piece_data, after_piece_data, move_number):
        if move_number in self.moves:
            raise Exception("Huh, apparently move_number %s already was set to %s. [game_id: %s, turn_id: %s]" % (move_number, self.moves[move_number], game_id, turn_id))
        else:
            self.moves[move_number] = (before_piece_data, after_piece_data)
