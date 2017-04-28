class Segment:
    def __init__(self, p1, p2, traj_id):
        self.cluster = -1
        self.id = id(self)
        self.p1 = p1
        self.p2 = p2
        self.traj_id = traj_id

    def __eq__(self, other):
        return self.id == other.id


class Cluster:
    def __init__(self):
        self.segments = []

    def add(self, s: Segment):
        self.segments += s