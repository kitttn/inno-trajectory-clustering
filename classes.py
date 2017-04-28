class Segment:
    def __init__(self, id, p1, p2):
        self.cluster = -1
        self.id = id
        self.p1 = p1
        self.p2 = p2

    def __eq__(self, other):
        return self.id == other.id
