import array


class Omino:
    def __init__(self, size):
        self.size = size
        self.grid = array.array("i", [0] * size * size)

    def __str__(self):
        ret = ""
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                ret = ret + str(self.get(x, y))
            ret = ret + "\n"
        return ret

    def __eq__(self, other):
        return self.grid == other.grid

    def set(self, x, y, value=1):
        self.grid[self.get_linear_coord(x, y)] = value

    def get(self, x, y):
        return self.grid[self.get_linear_coord(x, y)]

    def set_linear(self, i):
        self.grid[i] = 1

    def first_set_square(self):
        i = 0
        while self.grid[i] != 1:
            i = i + 1
        return i

    def get_xy_coord(self, i):
        """Takes a linear coordinate, i, and returns the x, y coordinates."""
        y = i // self.size
        x = i % self.size
        return x, y

    def get_linear_coord(self, x, y):
        """Take an x, y coordinate and return the linear coordinate."""
        return (self.size * y) + x

    def find_set_neighbours(self, sq):
        """Return a set of all the coloured-in neighbours of a square."""
        sx, sy = self.get_xy_coord(sq)
        neigh = []
        x = sx - 1
        y = sy
        if x >= 0:
            i = self.get_linear_coord(x, y)
            if self.grid[i] == 1:
                neigh.append(i)
        x = sx + 1
        y = sy
        if x <= self.size - 1:
            i = self.get_linear_coord(x, y)
            if self.grid[i] == 1:
                neigh.append(i)
        x = sx
        y = sy - 1
        if y >= 0:
            i = self.get_linear_coord(x, y)
            if self.grid[i] == 1:
                neigh.append(i)
        x = sx
        y = sy + 1
        if y <= self.size - 1:
            i = self.get_linear_coord(x, y)
            if self.grid[i] == 1:
                neigh.append(i)
        return set(neigh)

    def is_joined(self):
        """Test if all the squares in a grid are joined together."""
        sq = self.first_set_square()
        clump = {sq}
        neighbours = self.find_set_neighbours(sq)
        newSquares = neighbours.difference(clump)
        clump = clump.union(newSquares)
        while len(newSquares) > 0:
            sq = newSquares.pop()
            neighbours = self.find_set_neighbours(sq)
            new = neighbours.difference(clump)
            newSquares = newSquares.union(new)
            clump = clump.union(newSquares)
        if len(clump) == self.size:
            return True
        else:
            return False

    def translate_left(self):
        """Translate an omino one place to the left deleting the right column."""
        for y in range(self.size):
            for x in range(self.size - 1):
                self.set(x, y, self.get(x + 1, y))
            self.set(self.size - 1, y, 0)

    def translate_down(self):
        for x in range(self.size):
            for y in range(self.size - 1):
                self.set(x, y, self.get(x, y + 1))
            self.set(x, self.size - 1, 0)

    def is_left_empty(self):
        """Check whether the left most column is empty"""
        for y in range(self.size):
            if self.get(0, y) == 1:
                return False
        return True

    def is_bottom_empty(self):
        for x in range(self.size):
            if self.get(x, 0) == 1:
                return False
        return True

    def translate_to_corner(self):
        while self.is_left_empty():
            self.translate_left()
        while self.is_bottom_empty():
            self.translate_down()

    def get_reflection(self):
        r = Omino(self.size)
        for x in range(self.size):
            for y in range(self.size):
                c = self.get(x, y)
                r.set(y, x, c)
        return r

    def get_rotation(self):
        r = Omino(self.size)
        mid = (self.size - 1) / 2.0
        for x in range(self.size):
            for y in range(self.size):
                c = self.get(x, y)
                nx = x - mid
                ny = y - mid
                rx = -ny
                ry = nx
                rx += mid
                ry += mid
                r.set(int(rx), int(ry), c)
        r.translate_to_corner()
        return r

    def get_duplicates(self):
        d = OminoCollection(self.size)
        # create all rotations and translations
        d._store.append(self)
        rot = self.get_rotation()
        d._store.append(rot)
        rot = rot.get_rotation()
        d._store.append(rot)
        rot = rot.get_rotation()
        d._store.append(rot)

        ref = self.get_reflection()
        d._store.append(ref)
        rot = ref.get_rotation()
        d._store.append(rot)
        rot = rot.get_rotation()
        d._store.append(rot)
        rot = rot.get_rotation()
        d._store.append(rot)

        return d


class OminoCollection:
    def __init__(self, omino_size):
        self.size = omino_size
        self._store = []

    def __repr__(self):
        return "<Collection of {} {}-ominos>".format(len(self), self.size)

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def make_all(self):
        # this code will only work if size == 4
        assert self.size == 4, "you must do 4-ominos for the moment"
        sizeSq = self.size * self.size
        # make all the possible grids with the right number of squares coloured in
        for i in range(sizeSq - 3):
            for j in range(i + 1, sizeSq - 2):
                for k in range(j + 1, sizeSq - 1):
                    for m in range(k + 1, sizeSq):
                        om = Omino(self.size)
                        om.set_linear(i)
                        om.set_linear(j)
                        om.set_linear(k)
                        om.set_linear(m)
                        # check if the squares are joined up
                        if om.is_joined():
                            # if so, move it to the bottom left corner
                            om.translate_to_corner()
                            # put it in the collection
                            self._store.append(om)

        # at this point we have all the ominoes but with all the
        # duplicates from translation, rotation and reflection as well

        # This removes all the translation duplicates
        # Using while loops here because the size of the list changes
        # as we go through it.
        i = 0
        while i < len(self._store) - 1:
            j = i + 1
            while j < len(self._store):
                if self._store[i] == self._store[j]:
                    self._store.pop(j)
                else:
                    # If we didn't find a match then move j along one,
                    # otherwise we can leave j the same as the shapes have
                    # moved along one instead.
                    j += 1
            i += 1

        i = 0
        while i < len(self._store) - 1:
            # Take the ith omino and create all its reflections and rotations.
            duplicates = self._store[i].get_duplicates()
            for j in range(len(duplicates)):
                k = i + 1
                while k < len(self._store):
                    if self._store[k] == duplicates._store[j]:
                        self._store.pop(k)
                    else:
                        k += 1
            i += 1


if __name__ == "__main__":
    collection = OminoCollection(4)
    collection.make_all()
    print(collection)
    for omino in collection:
        print(omino)
