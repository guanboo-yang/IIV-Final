from itertools import pairwise, permutations
import sys
from typing import TextIO

from path import get_path


class Vehicle:
    def __init__(self, id: int, arrive_time: int, start: int, end: int, payment: int):
        self.id = id
        self.arrive_time = arrive_time
        self.start = start
        self.end = end
        self.payment = payment
        self.path: list[TCG_Node] = []

        for zone in get_path(start, end):
            node = TCG_Node(id, zone)
            self.path.append(node)

    def __repr__(self):
        return f"{' → '.join(map(str, self.path))}"


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

    def reverse(self):
        self.start, self.end = self.end, self.start
        # update outgoing list
        self.start.outgoing.append(self)
        self.end.outgoing.remove(self)

    def __repr__(self):
        return f"TCGE({self.type}, {self.start} → {self.end})"


class TCG:
    def __init__(self):
        super().__init__()
        self.nodes: list[TCG_Node] = []
        self.edges: list[TCG_Edge] = []
        self.vehicles: list[Vehicle] = []
        self.prev: list[Vehicle] = [None, None, None, None]  # prev vehicle for each zone

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
        for z in range(4):
            nodes = [node for node in self.nodes if node.zid == z]
            for n1, n2 in permutations(nodes, 2):
                edge1 = n1.link_to(n2, 3)
                self.edges.append(edge1)

    def solve(self):
        # remove type 3 edge: FCFS
        for e in self.edges:
            if e.type == 3:
                if e.start.vid > e.end.vid or e.start.vid == e.end.vid:
                    e.reverse()

    def topological_sort(self):
        zones = [[], [], [], []]

        for n in self.nodes:
            n.in_degree = 0

        # calculate in degree for all nodes
        for e in self.edges:
            e.end.in_degree += 1

        # print graph
        # print("nodes")
        # for n in self.nodes:
        #     print(n, n.in_degree)
        # print("\nedges")
        # for e in self.edges:
        #     print(e)

        zero_degree_nodes = [n for n in self.nodes if n.in_degree == 0]
        remaining_nodes = len(self.nodes)

        while remaining_nodes:
            m = len(zero_degree_nodes)
            for _ in range(m):
                n = zero_degree_nodes.pop()
                zones[n.zid].append(n)
                remaining_nodes -= 1
                for e in n.outgoing:
                    e.end.in_degree -= 1
                    if e.end.in_degree == 0:
                        zero_degree_nodes.append(e.end)

        return zones

    def schedule(self):
        result = self.topological_sort()
        ret = [[], [], [], []]
        for z in range(4):
            for n in result[z]:
                ret[z].append(n.vid)
        return ret

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

    def build_edge_dict(self, TCG: TCG):
        self.TCG_edge_dict = dict()
        for e in TCG.edges:
            self.TCG_edge_dict[(e.start.vid, e.start.zid, e.end.vid, e.end.zid)] = e.type

    def search_TCG_edge(self, vid1, zid1, vid2, zid2):
        if vid1 == None or vid2 == None:
            return None
        if self.TCG_edge_dict.get((vid1, zid1, vid2, zid2)) != None:
            return 0
        elif self.TCG_edge_dict.get((vid2, zid2, vid1, zid1)) != None:
            return 1
        else:
            return None

    def build(self, TCG: TCG):
        self.build_edge_dict(TCG)

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

        def add_edge(q_v1, q_start, q_v2, q_end):
            ret = self.search_TCG_edge(q_v1, q_start, q_v2, q_end)
            if ret == 0:
                RCG_edge = node1.link_to(node2)
                self.edges.append(RCG_edge)
            elif ret == 1:
                RCG_edge = node2.link_to(node1)
                self.edges.append(RCG_edge)

        # create the resource conflict graph edge according to the slide_6 p42 rule(b)~(e)
        for RCG_node_i in range(len(self.nodes)):
            for RCG_node_j in range(RCG_node_i, len(self.nodes)):
                node1 = self.nodes[RCG_node_i]
                node2 = self.nodes[RCG_node_j]
                if node1.vid != node2.vid:
                    q_v1, q_v2 = node1.vid, node2.vid
                    if node1.start == node2.start:
                        add_edge(q_v1, node1.start, q_v2, node2.start)
                    if node1.start == node2.end:
                        add_edge(q_v1, node1.start, q_v2, node2.end)
                    if node1.end == node2.start:
                        add_edge(q_v1, node1.end, q_v2, node2.start)
                    if node1.end == node2.end:
                        add_edge(q_v1, node1.end, q_v2, node2.end)

    def build_adj_list(self):
        self.adj_list = [[] for i in range(len(self.nodes))]
        for edge in self.edges:
            self.adj_list[self.nodes.index(edge.start)].append(self.nodes.index(edge.end))  # use original nodes index as the adj list index

    def dfs(self, v, visited, stack):
        visited[v] = True
        stack[v] = True

        for i in self.adj_list[v]:
            if not visited[i]:
                if self.dfs(i, visited, stack):
                    return True
            elif stack[i]:
                return True

        stack[v] = False
        return False

    def has_deadlock(self) -> bool:
        # TODO: check if there is a deadlock
        # check if this graph has a cycle
        # use DFS to check if there is a cycle
        self.build_adj_list()
        visited = [False] * len(self.nodes)
        stack = [False] * len(self.nodes)

        for v in range(len(self.nodes)):
            if not visited[v]:
                if self.dfs(v, visited, stack):
                    return True
        return False

    def __repr__(self):
        return f"RCG({len(self.nodes)} nodes, {len(self.edges)} edges)"


def main(input: TextIO):

    tcg = TCG()
    tcg.build(input)
    print(tcg)
    # print(*tcg.vehicles, sep="\n")
    # print(*tcg.edges, sep="\n")
    # print(*[e for e in tcg.edges if e.type == 2], sep="\n")

    # regenerate rcg until no deadlock
    while True:
        tcg.solve()
        rcg = RCG()
        rcg.build(tcg)
        if not rcg.has_deadlock():
            break
        print(f"{rcg} -> deadlock")

    print(rcg)
    # print(*rcg.nodes, sep="\n")
    # print(len(rcg.nodes))
    # print(len(rcg.edges))
    ret = tcg.schedule()
    # TODO: need to output this to some file
    for z in range(4):
        print(ret[z])


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
