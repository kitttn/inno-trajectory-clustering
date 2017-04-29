import math
from queue import Queue

import sympy as sp
from mpmath import *

from classes import Segment, Cluster, Trajectory

EPSILON = 1


def euclen(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** (1 / 2)


def eps_neigh(m: Segment, D, eps):
    N_eps = []
    for d in D:
        if d.id == m.id:
            continue
        else:
            if dist(m.line, d) < eps:
                N_eps.append(d)
    return N_eps


# perpendicular distance between points
def perpdist(l1: sp.Line, l2: sp.Line):
    p1 = l1.projection(l2.p1)
    p2 = l1.projection(l2.p2)
    # print("Points:", p1, p2)
    d1 = euclen(p1, l2.p1)
    d2 = euclen(p2, l2.p2)
    # print("Distance 1: ", d1)
    # print("Distance 2: ", d2)
    if d1 + d2 == 0:
        return 0
    return (d1 ** 2 + d2 ** 2) / (d1 + d2)


def pardist(l1: sp.Line, l2: sp.Line):
    p1 = l1.projection(l2.p1)
    p2 = l1.projection(l2.p2)
    # print("Points:", p1, p2)
    d1 = euclen(p1, l1.p1)
    d2 = euclen(p2, l1.p2)
    # print("Dist: ", d1, d2)
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


def line_segment_clustering(segments, eps: float, min_lines: int):
    cluster_id = 0
    queue = Queue()
    for L in segments:
        if L.cluster == -1:
            neighbs = eps_neigh(L, segments, EPSILON)
            if len(neighbs) >= min_lines:
                L.cluster = cluster_id
                filtered = list(filter(lambda x: x != L, neighbs))
                for x in filtered:
                    queue.put(x)
                expand_cluster(queue, segments, cluster_id, eps, min_lines)
                cluster_id += 1
            else:
                L.cluster = math.inf

    clusters = {}
    for L in segments:
        if L.cluster not in clusters:
            clusters[L.cluster] = Cluster()
        clusters[L.cluster].add(L)

    for _, cluster in clusters.items():
        participating = [seg.traj_id for seg in cluster.segments]
        PTR = len(set(participating))

        print("Count: ", PTR)
        if PTR < min_lines:
            del clusters[_]

    return clusters


def dist(l1: sp.Line, l2: sp.Line):
    return float(perpdist(l1, l2)) + float(angdist(l1, l2)) + float(pardist(l1, l2))


def mdlpar(t):
    def lh(ps: sp.Point2D, pe: sp.Point2D):
        return euclen(ps, pe) ** 2

    def ldh(pts):
        ps = pts[0]
        pe = pts[len(pts) - 1]
        perpsum = 0
        angsum = 0
        for i in range(0, len(pts) - 1):
            px = pts[i]
            py = pts[i + 1]
            perpsum += perpdist(sp.Line(ps, pe, evaluate=False), sp.Line(px, py, evaluate=False))
            angsum += angdist(sp.Line(ps, pe, evaluate=False), sp.Line(px, py, evaluate=False))

        return perpsum ** 2 + angsum ** 2

    return lh(t[0], t[len(t) - 1]) + ldh(t)


def mdlnopar(t):
    def lh(ps: sp.Point2D, pe: sp.Point2D):
        return euclen(ps, pe) ** 2

    return lh(t[0], t[len(t) - 1])


def expand_cluster(Q, D, cluster_id: int, eps: float, min_lines: int):
    while not Q.empty():
        N = eps_neigh(Q.get(), D, eps)
        if len(N) >= min_lines:
            for X in N:
                if X.cluster == -1 or X.cluster == math.inf:
                    X.cluster = cluster_id
                if X.cluster == -1:
                    Q.put(X)
        Q.get()


def traclus(trajectories):
    D = []
    num = 1
    for TR in trajectories:
        L = approx_trajectory_partitioning(TR)
        D += create_trajectory(num, L)
        print("Finished", num, "out of", len(trajectories))
        num += 1

    O = line_segment_clustering(D, EPSILON, 1)

    for key, value in O.items():
        print(key, ":", value)


def create_trajectory(id, points):
    output = []
    for i in range(0, len(points) - 1):
        seg = Segment(points[i], points[i + 1], id)
        output.append(seg)
    return output


def get_trajectories():
    curr = []
    arr = []

    f = open('paths.txt.copy', 'r')
    for line in f:
        if len(line) > 2:
            parsed = [float(x) for x in line.strip().split(" ")]
            nums = sp.Point2D(parsed[0], parsed[1], evaluate=False)
            curr.append(nums)
        else:
            # print(curr)
            arr.append(curr)
            curr = []
            break

    print("Read trajectories: ", len(arr))
    print("Example: ", arr[0])
    return arr


def approx_trajectory_partitioning(trajectory):
    output = [trajectory[0]]
    start, length = (0, 1)
    while start + length < len(trajectory):
        print("Processing", start + length, "out of", len(trajectory))
        curr = start + length
        traj = trajectory[start:curr + 1]
        costpar = mdlpar(traj)
        costnopar = mdlnopar(traj)
        if costpar > costnopar:
            output.append(trajectory[curr - 1])
            start = curr - 1
            length = 1
        else:
            length += 1

    output.append(trajectory[len(trajectory) - 1])
    return output


traj = get_trajectories()
traclus(traj)
