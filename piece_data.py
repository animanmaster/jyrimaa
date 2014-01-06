from functools import total_ordering

@total_ordering
class PieceData:
    MAX_RADIUS = 14

    def __init__(self):
        self.stronger_enemies = [0] * self.MAX_RADIUS
        self.stronger_friends = [0] * self.MAX_RADIUS
        self.weaker_enemies = [0] * self.MAX_RADIUS
        self.weaker_friends = [0] * self.MAX_RADIUS
        self.trap_distances = []
        self.boundary_distances = []
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
        '''
        For backwards compatibility with old code, this method is essentially get_hash with a default of r=4
        '''
        return self.get_hash(radius)

    def get_hash(self, radius=None):
        '''
        Hex data hash for this PieceData. The structure for a given radius will be like so in binary:

          0000     0000    0000      0000     0000         0000
          \___________/    \____________/     \__/         \__/
           |        |       |         |        |            |
        stronger  weaker   stronger  weaker   number      number
            friends            enemies         of           of
                                             boundaries   traps

        (total of 3 bytes [6 hex characters] to represent each aspect in the given radius)

        >>> pd.get_hash() # 00.00.02.00.0.1|00.02.00.01.0.0|01.00.03.01.2.1|00.10.00.00.2.1|00.01.01.01.0.0|01.00.00.00.0.0|01.00.00.00.0.1|02.00.00.00.0.0|00.00.00.08.0.0|00.00.00.00.0.0|01.00.00.00.0.0|05.00.00.04.0.0|00.00.00.00.0.0|00.00.01.00.0.0
        '0020010201001031210a0021011100100000100001200000000800000000100000500400000000001000'
        >>> pd.get_hash(4)
        '0020010201001031210a0021'
        '''
        if not self.hashed:
            zipped = zip(self.stronger_friends, self.weaker_friends, self.stronger_enemies, self.weaker_enemies)
            values = []
            for r in range(self.MAX_RADIUS):
                # Note r's range is [0, MAX_RADIUS), so r is actually the actual radius - 1.
                for radius_value in zipped[r]:
                    values.append(hex(radius_value)[-1])
                # Append the number of boundaries at this range.
                values.append(hex(self.boundary_distances.count(r+1))[-1])
                values.append(hex(self.trap_distances.count(r+1))[-1])
            self.hashed = ''.join(values)
        return radius and self.hashed[0:(6 * radius)] or self.hashed

    def radial_hashes(self):
        '''
        Return hashes for all radiuses between [1,MAX_RADIUS] inclusive.

        >>> pd.radial_hashes()
        ['002001', '002001020100', '002001020100103121', '0020010201001031210a0021', '0020010201001031210a0021011100', '0020010201001031210a0021011100100000', '0020010201001031210a0021011100100000100001', '0020010201001031210a0021011100100000100001200000', '0020010201001031210a0021011100100000100001200000000800', '0020010201001031210a0021011100100000100001200000000800000000', '0020010201001031210a0021011100100000100001200000000800000000100000', '0020010201001031210a0021011100100000100001200000000800000000100000500400', '0020010201001031210a0021011100100000100001200000000800000000100000500400000000', '0020010201001031210a0021011100100000100001200000000800000000100000500400000000001000']
        '''
        return map(lambda r: self.get_hash(r+1), range(self.MAX_RADIUS))

    def __eq__(self, other):
        '''
        Return hashes for all radiuses between [1,MAX_RADIUS] inclusive.

        >>> pd2 = PieceData()
        >>> pd2.stronger_friends = pd.stronger_friends
        >>> pd2.weaker_friends   = pd.weaker_friends
        >>> pd2.stronger_enemies = pd.stronger_enemies
        >>> pd2.weaker_enemies   = pd.weaker_enemies
        >>> pd2.boundary_distances = pd.boundary_distances
        >>> pd2.trap_distances     = pd.trap_distances

        >>> pd == pd2
        True
        >>> pd2 == pd
        True

        >>> pd2.stronger_enemies = [0] * len(pd2.stronger_enemies)
        >>> pd2.hashed = None
        >>> pd2 == pd
        False
        >>> pd == pd2
        False
        '''
        return isinstance(other, PieceData) and self.get_hash() == other.get_hash() or False

    def __lt__(self, other):
        '''
        Return hashes for all radiuses between [1,MAX_RADIUS] inclusive.

        >>> pd2 = PieceData()
        >>> pd2.stronger_friends = pd.stronger_friends
        >>> pd2.weaker_friends   = pd.weaker_friends
        >>> pd2.stronger_enemies = pd.stronger_enemies
        >>> pd2.weaker_enemies   = pd.weaker_enemies
        >>> pd2.boundary_distances = pd.boundary_distances
        >>> pd2.trap_distances     = pd.trap_distances

        >>> pd < pd2
        False
        >>> pd2 < pd
        False

        >>> pd2.stronger_enemies = [0] * len(pd2.stronger_enemies)
        >>> pd2.hashed = None
        >>> pd2 < pd
        True
        >>> pd < pd2
        False
        >>> sorted([pd2, pd]) == [pd2, pd]
        True
        >>> sorted([pd, pd2]) == [pd2, pd]
        True
        '''
        return isinstance(other, PieceData) and self.get_hash() < other.get_hash() or False

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

if __name__ == "__main__":
    import doctest
    pd = PieceData()
    pd.stronger_friends = [0, 0, 1, 0, 0, 1, 1, 2, 0, 0, 1, 5, 0, 0]
    pd.weaker_friends   = [0, 2, 0, 10, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    pd.stronger_enemies = [2, 0, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    pd.weaker_enemies   = [0, 1, 1, 0, 1, 0, 0, 0, 8, 0, 0, 4, 0, 0]
    pd.boundary_distances = [3, 3, 4, 4]
    pd.trap_distances     = [1, 3, 4, 7]
    doctest.testmod(extraglobs={'pd': pd})
