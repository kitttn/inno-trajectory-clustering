import math
from queue import Queue

import sympy as sp
from mpmath import *

from classes import Segment

EPSILON = 1


def euclen(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** (1 / 2)


def eps_neigh(m, D, eps):
    N_eps = []
    for d in D:
        if d.id == m.id:
            continue
        else:
            if dist(m, d) < eps:
                N_eps += d
    return N_eps


# perpendicluar distance between points
def perpdist(l1: sp.Line, l2: sp.Line):
    p1 = sp.Point2D(l1.projection(l2.p1))
    p2 = sp.Point2D(l1.projection(l2.p2))
    print("Points:", p1, p2)
    d1 = euclen(p1, l2.p1)
    d2 = euclen(p2, l2.p2)
    print("Distance 1: ", d1)
    print("Distance 2: ", d2)
    return (d1 ** 2 + d2 ** 2) / (d1 + d2)


def pardist(l1: sp.Line, l2: sp.Line):
    p1 = sp.Point2D(l1.projection(l2.p1))
    p2 = sp.Point2D(l1.projection(l2.p2))
    print("Points:", p1, p2)
    d1 = euclen(p1, l1.p1)
    d2 = euclen(p2, l1.p2)
    print("Dist: ", d1, d2)
    return min(d1, d2)


# angle distance between points?
def angdist(l1: sp.Line, l2: sp.Line):
    angle_r = float(l1.angle_between(l2))
    angle_g = mp.degrees(angle_r) % 180
    l2_length = euclen(l2.p1, l2.p2)
    if 0 <= angle_g < 90:
        return l2_length * math.sin(angle_g)
    else:
        return l2_length


def line_segment_clustering(trajectory, eps: float, min_lines: int):
    segments = [Segment(_, trajectory[_].p1, trajectory[_].p2) for _ in trajectory]
    clusterId = 0
    queue = Queue()
    for L in segments:
        if L.cluster == -1:
            neighbs = eps_neigh(L, segments, EPSILON)
            if len(neighbs) >= min_lines:
                L.cluster = clusterId
                filtered = filter(lambda x: x != L, neighbs)[:]
                queue += filtered
                expand_cluster(queue, segments, clusterId, eps, min_lines)
                clusterId += 1
            else:
                L.cluster = math.inf


def dist(l1: sp.Line, l2: sp.Line):
    return perpdist(l1, l2) + angdist(l1, l2) + pardist(l1, l2)


def mdlpar(t):
    def lh(ps: sp.Point2D, pe: sp.Point2D):
        return math.log(euclen(ps, pe))

    def ldh(pts):
        ps = pts[0]
        pe = pts[len(pts) - 1]
        perpsum = 0
        angsum = 0
        for i in range(0, len(pts) - 1):
            px = pts[i]
            py = pts[i + 1]
            perpsum += perpdist(sp.Line(ps, pe), sp.Line(px, py))
            angsum += angdist(sp.Line(ps, pe), sp.Line(px, py))

        return math.log(perpsum) + math.log(angsum)

    return lh(t[0], t[len(t) - 1]) + ldh(t)


def mdlnopar(t):
    def lh(ps: sp.Point2D, pe: sp.Point2D):
        return math.log(euclen(ps, pe))

    return lh(t[0], t[len(t) - 1])


def expand_cluster(Q, D, clusterId: int, eps: float, minLines: int):
    while not Q.empty():
        N = eps_neigh(Q.get())
        if len(N) >= minLines:
            for X in N:
                if X.cluster == -1 or X.cluster == math.inf:
                    X.cluster = clusterId
                if X.cluster == -1:
                    Q.put(X)
        Q.get()


def traclus(trajectories):
    for TR in trajectories:
        L = atp(TR)


def atp(trajectory):
    output = []
    output += trajectory[0]
    start, length = (0, 1)
    while start + length < len(trajectory):
        curr = start + length
        traj = trajectory[start:curr + 1]
        costpar = mdlpar(traj)
        costnopar = mdlnopar(traj)
        if costpar > costnopar:
            output += trajectory[curr - 1]
            start = curr - 1
            length = 1
        else:
            length += 1

    output += trajectory[len(trajectory) - 1]
    return output


l1 = sp.Line((1, 1), (5, 1))
l2 = sp.Line((2, 2), (4, 4))
d = angdist(l1, l2)
print(d)
