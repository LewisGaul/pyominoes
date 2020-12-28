import time


class Omino:
    def __init__(self, points):
        size, points = points.split("/")
        self.size = int(size)
        self.points = set()
        for p in points.split("."):
            self.points.add((int(p) % self.size, int(p) // self.size))

    def __str__(self):
        ret = ""
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                if (x, y) in self.points:
                    ret += "#"
                else:
                    ret += "."
            ret = ret + "\n"
        return ret[:-1]

    def __repr__(self):
        nums = sorted(p[0] + (p[1] * self.size) for p in self.points)
        ret = "{:d}/".format(self.size)
        for n in nums:
            ret += "{:3d}.".format(n)
        return ret[:-1]

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return repr(self) == repr(other)
        return super().__eq__(other)

    def __hash__(self):
        return hash(repr(self))

    def move_to_corner(self):
        minx = miny = 1e99  # big!
        for p in self.points:
            minx = min(minx, p[0])
            miny = min(miny, p[1])
        new_points = set()
        for p in self.points:
            new_points.add((p[0] - minx, p[1] - miny))
        self.points = new_points

    def rotate(self):
        new_points = set()
        for p in self.points:
            new_points.add((-p[1], p[0]))
        self.points = new_points
        self.move_to_corner()

    def transpose(self):
        new_points = set()
        for p in self.points:
            new_points.add((p[1], p[0]))
        self.points = new_points

    def copy(self):
        om = Omino(repr(self))
        return om

    def copy_bigger(self):
        om = self.copy()
        om.size = self.size + 1
        return om

    def get_neighbours(self):
        new_points = set()
        for p in self.points:
            new_points.add((p[0] - 1, p[1]))
            new_points.add((p[0] + 1, p[1]))
            new_points.add((p[0], p[1] - 1))
            new_points.add((p[0], p[1] + 1))
        return new_points.difference(self.points)

    def canonicalise(self):
        self.move_to_corner()
        rep = [repr(self)]
        for _ in range(3):
            self.rotate()
            rep.append(repr(self))
        self.transpose()
        rep.append(repr(self))
        for _ in range(3):
            self.rotate()
            rep.append(repr(self))
        rep.sort()
        om = Omino(rep[0])
        self.points = om.points


def next_set(old_set):
    new_set = set()
    for old_om in old_set:
        neighbours = old_om.get_neighbours()
        for neigh in neighbours:
            new_om = old_om.copy_bigger()
            # add trial neighbour to new_om
            new_om.points.add(neigh)
            new_om.canonicalise()
            new_set.add(new_om)
    return new_set


def print_omino_set(om_set, filename, num_columns=160):
    om_list = sorted(repr(om) for om in om_set)
    om = om_list[0]
    size = int(om.split("/")[0])
    num_on_line = num_columns // size

    line_buffer = ["" for _ in range(size)]
    with open(filename, "w") as f:
        c = 1
        for om in om_list:
            om_str = str(Omino(om))
            om_lines = om_str.split("\n")
            for i in range(size):
                line_buffer[i] += om_lines[i] + " "
            if c % num_on_line == 0:
                for line in line_buffer:
                    if "#" in line:
                        f.write(line[:-1] + "\n")
                f.write("\n")
                line_buffer = ["" for i in range(size)]
            c += 1
        if c % num_on_line != 1:
            for line in line_buffer:
                if "#" in line:
                    f.write(line[:-1] + "\n")


if __name__ == "__main__":
    omino = Omino("1/0")
    s = {omino}
    i = 1
    t0 = t1 = time.time()
    while True:
        t2 = time.time()
        print(
            "Found {} polyomino(es) of size {} ({:.2f}s / {:.2f}s)".format(
                len(s), i, t2 - t1, t2 - t0
            )
        )
        if len(s) < 10:
            for om in s:
                print(om)
        print_omino_set(s, "{}ominoes.txt".format(i))
        t1 = t2
        s = next_set(s)
        i += 1
