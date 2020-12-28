class Omino:
    def __init__(self, size):
        self._points = set()
        self.size = size

    def __str__(self):
        ret = ""
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                if (x, y) in self._points:
                    ret += "#"
                else:
                    ret += "."
            ret = ret + "\n"
        return ret

    def _as_tuple(self):
        lst = []
        for p in self._points:
            lst.append(p[0] + (p[1] * self.size))
        lst.sort()
        return tuple(lst)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._as_tuple() == other._as_tuple()
        return super().__eq__(other)

    def __hash__(self):
        return hash(self._as_tuple())

    def move_to_corner(self):
        minx = miny = 1e99  # big!
        for p in self._points:
            minx = min(minx, p[0])
            miny = min(miny, p[1])
        new_points = set()
        for p in self._points:
            new_points.add((p[0] - minx, p[1] - miny))
        self._points = new_points

    def rotate(self):
        new_points = set()
        for p in self._points:
            new_points.add((-p[1], p[0]))
        self._points = new_points
        self.move_to_corner()

    def transpose(self):
        new_points = set()
        for p in self._points:
            new_points.add((p[1], p[0]))
        self._points = new_points

    def copy(self):
        om = Omino(self.size)
        om._points = set(self._points)
        return om

    def copy_bigger(self):
        om = self.copy()
        om.size = self.size + 1
        return om

    def get_neighbours(self):
        new_points = set()
        for p in self._points:
            new_points.add((p[0] - 1, p[1]))
            new_points.add((p[0] + 1, p[1]))
            new_points.add((p[0], p[1] - 1))
            new_points.add((p[0], p[1] + 1))
        return new_points.difference(self._points)


def get_rot_and_mirror(om):
    om_set = {om}
    omr = om.copy()
    omr.rotate()
    om_set.add(omr)
    omr = omr.copy()
    omr.rotate()
    om_set.add(omr)
    omr = omr.copy()
    omr.rotate()
    om_set.add(omr)
    omt = om.copy()
    omt.transpose()
    if omt in om_set:
        return om_set
    om_set.add(omt)
    omt = omt.copy()
    omt.rotate()
    om_set.add(omt)
    omt = omt.copy()
    omt.rotate()
    om_set.add(omt)
    omt = omt.copy()
    omt.rotate()
    om_set.add(omt)
    return om_set


def next_set(old_set):
    newSet = set()
    for om in old_set:
        neighbours = om.get_neighbours()
        for neigh in neighbours:
            new_om = om.copy_bigger()
            # add trial neighbour to newOm
            new_om._points.add(neigh)
            # add newOm to newSet
            new_om.move_to_corner()
            om_set = get_rot_and_mirror(new_om)
            if om_set.isdisjoint(newSet):
                newSet.add(new_om)
    return newSet


if __name__ == "__main__":
    omino = Omino(1)
    omino._points.add((0, 0))
    s = {omino}
    i = 1
    while True:
        print("Found {} polyomino(es) of size {}".format(len(s), i))
        if len(s) < 10:
            for om in s:
                print(om)
        s = next_set(s)
        i += 1
