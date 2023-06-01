class Edge:
    def __init__(self, name):
        self._name = name
        self._quantification = 0.00

    def get_name(self):
        return self._name

    def get_quantification(self):
        return self._quantification

    def set_quantification(self, value):
        self._quantification = float(value)


class Cause(Edge):
    def __init__(self, name):
        super().__init__(name)


class Consequence(Edge):
    def __init__(self, name):
        super().__init__(name)
