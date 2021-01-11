import time
from collections import namedtuple
from typing import Set

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm

    pdf_support = True
except ImportError:
    pdf_support = False


Point = namedtuple("Point", "x, y")


class Omino:
    def __init__(self, points: str):
        """
        :param points:
            The points representation, of the form:
            "<size>/ <point> . <point> . ..."
            e.g. "3/0.3.4".
        """
        size, points = points.split("/")
        self.size: int = int(size)
        self.points: Set[Point] = {
            Point(int(p) % self.size, int(p) // self.size) for p in points.split(".")
        }

    def __str__(self):
        lines = []
        for y in range(self.size):
            lines.append(
                "".join(
                    "#" if Point(x, y) in self.points else "." for x in range(self.size)
                )
            )
        return "\n".join(reversed(lines))

    def __repr__(self):
        nums = sorted(p.x + (p.y * self.size) for p in self.points)
        points = ".".join("{:3d}".format(n) for n in nums)
        return "{:d}/{}".format(self.size, points)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return repr(self) == repr(other)
        return super().__eq__(other)

    def __hash__(self):
        return hash(repr(self))

    def move_to_corner(self) -> None:
        """
        In-place move into the bottom-left corner (minimise x and y coords).
        """
        min_x = min(self.points, key=lambda p: p.x).x
        min_y = min(self.points, key=lambda p: p.y).y
        self.points = {Point(p.x - min_x, p.y - min_y) for p in self.points}

    def rotate(self) -> None:
        """
        In-place rotate 90 degrees anti-clockwise and shift to the corner.
        """
        self.points = {Point(-p.y, p.x) for p in self.points}
        self.move_to_corner()

    def transpose(self) -> None:
        """
        In-place switch x and y coordinates (reflect in the line y=x).
        """
        self.points = {Point(p.y, p.x) for p in self.points}

    def copy(self) -> "Omino":
        return Omino(repr(self))

    # @@@ This returns an inconsistent object.
    def copy_bigger(self) -> "Omino":
        """
        Create a copy and increment the size by one.
        """
        om = self.copy()
        om.size = self.size + 1
        return om

    def get_free_neighbours(self) -> Set[Point]:
        """
        Get a set of available points adjacent to occupied points.
        """
        new_points = set()
        for p in self.points:
            new_points.add(Point(p.x - 1, p.y))
            new_points.add(Point(p.x + 1, p.y))
            new_points.add(Point(p.x, p.y - 1))
            new_points.add(Point(p.x, p.y + 1))
        return new_points - self.points

    def canonicalise(self) -> None:
        """
        In-place transform to canonical representation.
        """
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
        om = Omino(min(rep))
        self.points = om.points


def next_set(old_set):
    new_set = set()
    for old_om in old_set:
        neighbours = old_om.get_free_neighbours()
        for neigh in neighbours:
            new_om = old_om.copy_bigger()
            # add trial neighbour to new_om
            new_om.points.add(neigh)
            new_om.canonicalise()
            new_set.add(new_om)
    return new_set


def print_omino_set(om_set, filename, num_columns=160):
    size = next(iter(om_set)).size
    num_on_line = num_columns // size

    line_buffer = ["" for _ in range(size)]
    with open(filename, "w") as f:
        c = 1
        for om in sorted(om_set, key=lambda x: repr(x)):
            om_str = str(om)
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


def print_omino_set_pdf(om_set, filename):
    num_per_row = 6
    size = next(iter(om_set)).size
    c = canvas.Canvas(filename)
    c.setStrokeColorRGB(1, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    sq = cm / 2
    i = 0
    for om in sorted(om_set, key=lambda x: repr(x)):
        offx = (i % num_per_row) * sq * (size + 1) + cm
        offy = (i // num_per_row) * sq * (size + 1) + cm
        for p in om.points:
            x, y = p
            c.rect(offx + (x * sq), offy + (y * sq), sq, sq)
        i += 1
    c.showPage()
    c.save()


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
        if pdf_support:
            print_omino_set_pdf(s, "{}ominoes.pdf".format(i))
        t1 = t2
        s = next_set(s)
        i += 1
