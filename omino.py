from array import array


class Omino:
    def __init__(self, size: int):
        self.size = size
        self.array = array("i", [1] * size * size)

    def __str__(self):
        ret = ""
        for x in range(0, self.size):
            for y in range(0, self.size):
                if self.array[x * self.size + y] == 1:
                    ret += "#"
                else:
                    ret += " "
            ret += "\n"
        return ret


if __name__ == "__main__":
    print(Omino(4))
