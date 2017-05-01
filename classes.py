import json
from typing import List
import sympy as sp

class Segment:
    def __init__(self, p1, p2, traj_id):
        self.cluster = -1
        self.id = id(self)
        self.p1 = p1
        self.p2 = p2
        self.line = sp.Line(self.p1, self.p2, evaluate = False)
        self.traj_id = traj_id

    def __eq__(self, other):
        return self.id == other.id

    def __unicode__(self):
        return " {id: %d, [%s, %s], clust: %d} " % (self.id, str(self.p1), str(self.p2), self.cluster)

    def __str__(self):
        return self.__unicode__()


class Trajectory:
    def __init__(self, id, points: List[Segment]):
        self.id = id
        self.points = points


class Cluster:
    def __init__(self, clust_id):
        self.clust_id = clust_id
        self.segments = []

    def add(self, s: Segment):
        self.segments.append(s)

    def __unicode__(self):
        res = ""
        for x in self.segments:
            res += str(x)
        return res

    def __str__(self):
        return self.__unicode__()
