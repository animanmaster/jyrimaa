
class PieceData:
    def __init__(self):
        self.stronger_enemies = [0] * 14
        self.stronger_friends = [0] * 14
        self.weaker_enemies = [0] * 14
        self.weaker_friends = [0] * 14
        self.hashed = None

    def add_friend(self, is_weaker, distance):
        if is_weaker:
            self.weaker_friends[distance - 1] += 1
        else:
            self.stronger_friends[distance - 1] += 1

    def add_enemy(self, is_weaker, distance):
        if is_weaker:
            self.weaker_enemies[distance - 1] += 1
        else:
            self.stronger_enemies[distance - 1] += 1

    def get_filtered_state(self, radius=4):
        stronger = ''.join([('%02d%02d' % (self.stronger_enemies[i], self.stronger_friends[i])) for i in range(radius)])
        weaker = ''.join([('%02d%02d' % (self.weaker_enemies[i], self.weaker_friends[i])) for i in range(radius)])
        traps = ''.join([d <= radius and ('%02d' % d) or '00' for d in self.trap_distances])
        boundaries = ''.join([d <= radius and ('%02d' % d) or '00' for d in self.boundary_distances])
        self.hashed = ''.join([stronger, weaker, traps, boundaries])
        return self.hashed

    def __str__(self):
        return """<html>
        <table>
        <tr>
        <td>Stronger friends by distance:</td>
            <td>%s</td>
        </tr><tr>
        <td>Stronger enemies by distance:</td>
            <td>%s</td>
        </tr><tr>
        <td>Weaker friends by distance:</td>
            <td>%s</td>
        </tr><tr>
        <td>Weaker enemies by distance:</td>
            <td>%s</td>
        </tr><tr>
        <td>Trap distances:</td>
            <td>%s</td>
        </tr><tr>
        <td>Boundary Distances:</td>
            <td>%s</td>
        </tr></table></html>
        """ % (self.stronger_friends, self.stronger_enemies, self.weaker_friends, self.weaker_enemies, self.trap_distances, self.boundary_distances)
