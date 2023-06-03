class Edge:
    def __init__(self, name):
        self._name = name
        self._probability = None

    def get_name(self):
        return self._name

    def get_probability(self):
        return self._probability

    def set_probability(self, value):
        self._probability = round(value, 8)


class Cause(Edge):
    def __init__(self, name):
        super().__init__(name)


class Consequence(Edge):
    def __init__(self, name):
        super().__init__(name)
        self._ratio = 0

    def get_ratio(self):
        return self._ratio

    def set_ratio(self, value):
        self._ratio = value


