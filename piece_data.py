
class PieceData:
    MAX_RADIUS = 14

    def __init__(self):
        self.stronger_enemies = [0] * MAX_RADIUS
        self.stronger_friends = [0] * MAX_RADIUS
        self.weaker_enemies = [0] * MAX_RADIUS
        self.weaker_friends = [0] * MAX_RADIUS
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

    def get_hash(self, radius=None):
        if not self.hashed:
            zipped = zip(self.stronger_friends, self.weaker_friends, self.stronger_enemies, self.weaker_enemies)
            values = []
            for r in range(MAX_RADIUS):
                # Note r's range is [0, MAX_RADIUS), so r is actually the actual radius - 1.
                for radius_value in zipped[r]:
                    values.append('%02d' % radius_value)
                # Append the number of boundaries at this range.
                values.append(str(self.boundary_distances.count(r)))
                values.append(str(self.trap_distances.count(r)))
            self.hashed = ''.join(values)
        return self.hashed[0:(radius and 10 * radius or None)]

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
        </tr><tr>
        <td>Full Hash:</td>
            <td>%s</td>
        </tr>
        </table></html>
        """ % (self.stronger_friends, self.stronger_enemies, self.weaker_friends, self.weaker_enemies,
               self.trap_distances, self.boundary_distances, self.get_hash())
