import asyncio
import math
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue
from typing import List

import sympy as sp
from mpmath import *

from classes import Segment, Cluster

EPSILON = 1
MIN_LINES = 3


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


def process_segment(L, segments, cluster_id):
    queue = Queue()
    if L.cluster == -1:
        print("Calculating neighbors...")
        neighbs = eps_neigh(L, segments, EPSILON)
        # print("Neighbors: %s" % neighbs)
        if len(neighbs) >= MIN_LINES:
            print("Creating cluster...")
            L.cluster = cluster_id
            filtered = list(filter(lambda x: x != L, neighbs))
            for x in filtered:
                queue.put(x)
            sout("[Expanding cluster...]")
            expand_cluster(queue, segments, cluster_id, eps, MIN_LINES)
            sout("[Expansion successful!]")
        else:
            L.cluster = math.inf
    else:
        sout("[Already processed!]")


async def line_segment_clustering(segments) -> List[Cluster]:
    total = len(segments)
    sout("S Total: %d" % total)
    els = [loop.run_in_executor(executor, process_segment, segments[_], segments, _) for _ in range(total)]
    await asyncio.gather(*els)

    clusters = {}
    for L in segments:
        clustId = L.cluster
        if clustId == math.inf:
            continue

        if L.cluster not in clusters:
            sout("[Adding clusterId=%d]" % L.cluster)
            clusters[L.cluster] = Cluster(L.cluster)
        clusters[L.cluster].add(L)

    result = []

    for _, cluster in clusters.items():
        participating = [seg.traj_id for seg in cluster.segments]
        PTR = len(set(participating))

        if PTR >= MIN_LINES:
            result.append(cluster)
        else:
            sout("[Not added, size=%d]" % PTR)

    return result


def sout(data):
    print("{%s}:%s" % (threading.current_thread().getName(), data))


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
        print("{%s}:[ Q size: %d ]" % (threading.current_thread().getName(), Q.qsize()))
        N = eps_neigh(Q.get(), D, eps)
        # print("{%s}:[ N size: %d ]" % (threading.current_thread().getName(), len(N)))
        if len(N) >= min_lines:
            for X in N:
                if X.cluster == -1 or X.cluster == math.inf:
                    Q.put(X)
                    X.cluster = cluster_id


async def traclus(trajectories):
    D = []
    num = 1

    LS = [loop.run_in_executor(executor, approx_trajectory_partitioning, TR) for TR in trajectories]
    els_processed = await asyncio.gather(*LS)

    for TR in els_processed:
        print("creating trajectory...")
        D += create_trajectory(num, TR)
        print("Finished", num, "out of", len(trajectories))
        num += 1

    O = await line_segment_clustering(D)

    for cluster in O:
        print(cluster.clust_id, ":", cluster.segments)


def create_trajectory(id, points):
    output = []
    for i in range(0, len(points) - 1):
        seg = Segment(points[i], points[i + 1], id)
        output.append(seg)
    return output


def get_trajectories():
    curr = []
    arr = []

    f = open('paths.txt', 'r')
    for line in f:
        if len(line) > 2:
            parsed = [float(x) for x in line.strip().split(" ")]
            nums = sp.Point2D(parsed[0], parsed[1], evaluate=False)
            curr.append(nums)
        else:
            # print(curr)
            arr.append(curr)
            curr = []

    if len(curr) > 0:
        arr.append(curr)

    print("Read trajectories: ", len(arr))
    print("Example: ", arr[0])
    return arr


def approx_trajectory_partitioning(trajectory):
    print("approximating...")
    output = [trajectory[0]]
    start, length = (0, 1)
    total = len(trajectory)
    while start + length < len(trajectory):
        print("{%s}:[%d/%d]" % (threading.current_thread().getName(), start, total))
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


async def run():
    traj = get_trajectories()
    await traclus(traj)


executor = ThreadPoolExecutor(32, "Thread")
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
