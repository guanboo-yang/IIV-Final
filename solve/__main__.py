from argparse import ArgumentParser
from enum import Enum
from itertools import combinations, pairwise, permutations
from queue import Queue
from random import random
import sys
from typing import TextIO

from path import get_path

# define constants
TIME_ENTER_ZONE = 1.4
TIME_CHANGE_ZONE = 0.85
TIME_WAIT = 0.2


class Vehicle:
    def __init__(self, id: int, arrive_time: int, start: int, end: int, payment: int):
        self.id = id
        self.arrive_time = arrive_time
        self.start = start
        self.end = end
        self.payment = payment
        self.path: list[TCG_Node] = []

        for zone in get_path(start, end):
            node = TCG_Node(id, zone, arrive_time)
            self.path.append(node)

    def __repr__(self):
        return f"{' → '.join(map(str, self.path))}"


class TCG_Node:
    def __init__(self, vid: int, zid: int, time: int):
        super().__init__()
        self.vid = vid
        self.zid = zid
        self.outgoing: list[TCG_Edge] = []
        self.in_degree = 0
        self.time = time + TIME_ENTER_ZONE

    def link_to(self, other: "TCG_Node", type: int):
        edge = TCG_Edge(type, self, other)
        self.outgoing.append(edge)
        return edge

    def __repr__(self):
        return f"({self.vid}, {self.zid})"


class TCG_Edge:
    def __init__(self, type: int, start: TCG_Node, end: TCG_Node):
        self.type = type
        self.start = start
        self.end = end

    def reverse(self):
        self.start, self.end = self.end, self.start
        # update outgoing list
        self.start.outgoing.append(self)
        self.end.outgoing.remove(self)

    def __repr__(self):
        return f"TCGE({self.type}, {self.start} → {self.end})"

    def __eq__(self, other: tuple[int, int, int, int]):
        return (self.start.vid, self.start.zid, self.end.vid, self.end.zid) == other

    def __hash__(self):
        return hash((self.start.vid, self.start.zid, self.end.vid, self.end.zid))


class TCG:
    def __init__(self):
        super().__init__()
        self.nodes: list[TCG_Node] = []
        self.edges: list[TCG_Edge] = []
        self.vehicles: list[Vehicle] = []
        self.prev: list[Vehicle] = [None, None, None, None]  # prev vehicle for each zone
        self.zone_times: list[int] = [0, 0, 0, 0]

    def build(self, input: TextIO):
        # keep reading until eof
        # handle type 1 edge and type 2 edge
        for line in input:
            vehicle = Vehicle(*map(int, line.split()))
            self.add_vehicle(vehicle)
        # handle type 3 edge
        self.build_type_3_edge()

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        # add nodes to graph
        for node in vehicle.path:
            self.nodes.append(node)
        # handle type 1 edge
        for start, end in pairwise(vehicle.path):
            edge = start.link_to(end, 1)
            self.edges.append(edge)
        # handle type 2 edge
        if self.prev[vehicle.start] is not None:
            for node1, node2 in zip(vehicle.path, self.prev[vehicle.start].path):
                edge = node2.link_to(node1, 2)
                self.edges.append(edge)
        self.prev[vehicle.start] = vehicle

    def build_type_3_edge(self):
        for zid in range(4):
            nodes = [node for node in self.nodes if node.zid == zid]
            for node1, node2 in combinations(nodes, 2):
                if self.vehicles[node1.vid].path[0].zid != self.vehicles[node2.vid].path[0].zid:
                    edge = node2.link_to(node1, 3)
                    self.edges.append(edge)

    def solve(self, method: str):
        if method == "fcfs":
            for edge in self.edges:
                if edge.type == 3 and edge.start.vid > edge.end.vid:
                    edge.reverse()
        if method == "random":
            for edge in self.edges:
                if edge.type == 3 and edge.start.vid > edge.end.vid and random() < 0.5:
                    edge.reverse()

    def schedule(self):
        # topological sort
        zones: list[list[TCG_Node]] = [[], [], [], []]
        # reset in degree
        for node in self.nodes:
            node.in_degree = 0
        # calculate in degree for each node
        for edge in self.edges:
            edge.end.in_degree += 1
        # find source nodes
        queue: Queue[TCG_Node] = Queue()
        for node in self.nodes:
            if node.in_degree == 0:
                queue.put(node)
        while not queue.empty():
            node = queue.get()
            zones[node.zid].append(node)
            for edge in node.outgoing:
                edge.end.in_degree -= 1
                # add to queue if in degree is 0
                if edge.end.in_degree == 0:
                    queue.put(edge.end)
            self.zone_times[node.zid] = max(self.zone_times[node.zid], node.time)
        return zones

    def __repr__(self):
        return f"TCG({len(self.vehicles)} vehicles, {len(self.nodes)} nodes, {len(self.edges)} edges)"


class Color(Enum):
    WHITE = 0  # unvisited
    GRAY = 1  # visited
    BLACK = 2  # finished


class RCG_Node:
    def __init__(self, vid: int, start: int, end: int):
        self.vid = vid
        self.start = start
        self.end = end
        self.color = Color.WHITE
        self.outgoing: list["RCG_Edge"] = []

    def link_to(self, other: "RCG_Node"):
        edge = RCG_Edge(self, other)
        self.outgoing.append(edge)
        return edge

    def __repr__(self):
        return f"({self.vid}, {self.start}, {self.end})"


class RCG_Edge:
    def __init__(self, start: "RCG_Node", end: "RCG_Node"):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"RCGE({self.start} → {self.end})"


class RCG:
    def __init__(self):
        self.nodes: list[RCG_Node] = []
        self.edges: list[RCG_Edge] = []
        # start_vid, start_zid, end_vid, end_zid
        self.TCG_edges: dict[tuple[int, int, int, int], int] = {}

    def build(self, tcg: TCG):
        # create TCG edges dict for fast search
        self.TCG_edges = {}
        for edge in tcg.edges:
            self.TCG_edges[edge] = edge.type

        # create RCG nodes from TCG type 1 edges
        for edge in tcg.edges:
            if edge.type == 1:
                node = RCG_Node(edge.start.vid, edge.start.zid, edge.end.zid)
                self.nodes.append(node)

        def add_edge(vid1, zid1, vid2, zid2):
            if self.TCG_edges.get((vid1, zid1, vid2, zid2)) != None:
                edge = node1.link_to(node2)
                self.edges.append(edge)

        # create RCG edges from TCG type 2 and 3 edges
        for node1, node2 in permutations(self.nodes, 2):
            # create the RCG edges (type a)
            if node1.vid == node2.vid:
                add_edge(node1.vid, node1.start, node2.vid, node2.start)
                continue
            # create the RCG edges (type b)
            add_edge(node1.vid, node1.start, node2.vid, node2.start)
            # create the RCG edges (type c)
            add_edge(node1.vid, node1.end, node2.vid, node2.end)
            # create the RCG edges (type d)
            add_edge(node1.vid, node1.start, node2.vid, node2.end)
            # create the RCG edges (type e)
            add_edge(node1.vid, node1.end, node2.vid, node2.start)

    # return True if there is a cycle
    def dfs(self, node: RCG_Node) -> bool:
        node.color = Color.GRAY
        for edge in node.outgoing:
            if edge.end.color == Color.GRAY:
                return True
            if edge.end.color == Color.WHITE:
                if self.dfs(edge.end):
                    return True
        node.color = Color.BLACK
        return False

    def has_deadlock(self) -> bool:
        # use DFS to check if there is a cycle
        for node in self.nodes:
            if self.dfs(node):
                return True
        return False

    def __repr__(self):
        return f"RCG({len(self.nodes)} nodes, {len(self.edges)} edges)"


def main(input: TextIO, output: TextIO, strategy: str):

    tcg = TCG()
    tcg.build(input)
    print(tcg)
    # print(*tcg.vehicles, sep="\n")
    # print(*tcg.edges, sep="\n")
    # print(*[edge for edge in tcg.edges], sep="\n")

    # regenerate rcg until no deadlock
    while True:
        tcg.solve(strategy)
        rcg = RCG()
        rcg.build(tcg)
        if not rcg.has_deadlock():
            break
        print(f"{rcg} -> deadlock")

    print(rcg)
    # print(*rcg.edges, sep="\n")

    schedule = tcg.schedule()

    for zid in range(4):
        print(zid, *[f"({node.vid}, {node.time:.2f})" for node in schedule[zid]], sep=" ")
        output.write(" ".join([str(node.vid) for node in schedule[zid]]) + "\n")


# parse arguments
def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-s", "--strategy", type=str, default="fcfs", help="scheduling strategy")
    parser.add_argument("-i", "--input", type=str, default=None, help="input file")
    parser.add_argument("-o", "--output", type=str, default=None, help="output file")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    input = open(args.input) if args.input else sys.stdin
    output = open(args.output, "w") if args.output else sys.stdout

    main(input, output, args.strategy)

    if input != sys.stdin:
        input.close()
    if output != sys.stdout:
        output.close()
