from itertools import permutations
import sys
from typing import TextIO

from path import get_path


class Vehicle:
    def __init__(self, id, arrive_time, start, end, payment):
        self.id = id
        self.arrive_time = arrive_time
        self.start = start
        self.end = end
        self.payment = payment

        self.path = get_path(start, end)

    def __repr__(self):
        return f"Vehicle({self.id}, {' → '.join(map(str, self.path))})"


class TCG_Node:
    def __init__(self, vid: int, zid: int):
        super().__init__()
        self.vid = vid
        self.zid = zid
        self.outgoing: list[TCG_Edge] = []

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

    def __repr__(self):
        return f"TCGE({self.start} → {self.end})"


class TCG:
    def __init__(self):
        super().__init__()
        self.vehicles: list[Vehicle] = []
        self.nodes: list[TCG_Node] = []
        self.edges: list[TCG_Edge] = []
        self.prev_vehicle: list[TCG_Node] = [None, None, None, None]
        self.zone_vehicles: list[list[TCG_Node]] = [[], [], [], []]

    def build(self, input: TextIO):
        # keep reading until eof
        for line in input:
            self.add_vehicle(Vehicle(*map(int, line.split())))
        # handle type 3 edge
        self.build_type_3_edge()

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        start = TCG_Node(vehicle.id, vehicle.start)

        # handle type 1 edge
        curr = start
        self.nodes.append(curr)  # add start node
        self.zone_vehicles[vehicle.start].append(curr)
        for z in vehicle.path[1:]:
            end = TCG_Node(vehicle.id, z)
            self.nodes.append(end)
            edge = curr.link_to(end, 1)
            self.edges.append(edge)
            curr = end
            self.zone_vehicles[z].append(curr)

        # handle type 2 edge
        if self.prev_vehicle[vehicle.start] is not None:
            edge = self.prev_vehicle[vehicle.start].link_to(start, 2)
            self.edges.append(edge)
        self.prev_vehicle[vehicle.start] = start

    def build_type_3_edge(self):
        for z in range(4):
            nodes = self.zone_vehicles[z]
            for n1, n2 in permutations(nodes, 2):
                edge = n1.link_to(n2, 3)
                self.edges.append(edge)

    def solve(self):
        # TODO: remove type 3 edge
        pass

    def __repr__(self):
        return f"TCG({len(self.vehicles)} vehicles, {len(self.nodes)} nodes, {len(self.edges)} edges)"


class RCG_Node:
    def __init__(self, vid: int, start: int, end: int):
        self.vid = vid
        self.start = start
        self.end = end
        self.outgoing: list["TCG_Edge"] = []

    def link_to(self, other: "RCG_Node"):
        RCG_edge = RCG_Edge(self, other)
        self.outgoing.append(RCG_edge)
        return RCG_edge

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

    def build(self, TCG: TCG):
        for graph_edge in TCG.edges:
            # create the conflict graph node
            if graph_edge.type == 1:
                RCG_start = RCG_Node(graph_edge.start.vid, graph_edge.start.zid, graph_edge.end.zid)
                self.nodes.append(RCG_start)

        # create the resource conflict graph edge according to the slide_6 p42 rule(a)
        for RCG_node_ind in range(len(self.nodes)):
            cur_id = self.nodes[RCG_node_ind].vid
            while (RCG_node_ind + 1 < len(self.nodes)) and self.nodes[RCG_node_ind + 1].vid == cur_id:
                RCG_edge = self.nodes[RCG_node_ind].link_to(self.nodes[RCG_node_ind + 1])
                RCG_node_ind = RCG_node_ind + 1
                self.edges.append(RCG_edge)
        # TODO: create the resource conflict graph edge according to the slide_6 p42 rule(b)~(e)

    def has_deadlock(self) -> bool:
        # TODO: check if there is a deadlock
        return False

    def __repr__(self):
        return f"RCG({len(self.nodes)} nodes, {len(self.edges)} edges)"


def main(input: TextIO):

    tcg = TCG()
    tcg.build(input)
    print(tcg)

    # regenerate rcg until no deadlock
    while True:
        tcg.solve()
        rcg = RCG()
        rcg.build(tcg)
        if not rcg.has_deadlock():
            break
        print(f"{rcg} -> deadlock")

    print(rcg)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: python3 solve file")
        exit(1)
    if len(args) == 1:
        input = open(args[0])
    else:
        input = sys.stdin

    main(input)

    if len(args) == 1:
        input.close()