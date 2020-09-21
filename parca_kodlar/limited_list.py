from statistics import mean


class LimitedList:
    def __init__(self, max_size=0):
        self._elements = []
        self.max_size = max_size

    def append(self, new_element):
        if self.max_size == len(self._elements):
            self._elements.append(new_element)
            return self._elements.pop(0)
        elif self.max_size > len(self._elements):
            self._elements.append(new_element)
            return None

    def mean(self, last=0):
        if last == 0 or last > len(self._elements):
            return mean(self._elements)
        return mean(self._elements[-last:])

    def get_items(self, last=0):
        if last == 0 or last > len(self._elements):
            return self._elements
        return self._elements[-last:]

    def __getitem__(self, key):
        return self._elements.__getitem__(key)

    def __setitem__(self, key, value):
        return self._elements.__setitem__(key, value)

    def __str__(self):
        return self._elements.__str__()


if __name__ == '__main__':
    l = LimitedList(5)
    for i in range(10):
        l.append(i)
        print(l)
    print(l.mean())
    print(l[3])
    print(l[1:4])

    print("mean", l.mean(0))
