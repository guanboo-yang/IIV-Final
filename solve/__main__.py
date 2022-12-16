from path import get_path
import sys


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
        self.vid = vid
        self.zid = zid
        self.outgoing: list["TCG_Edge"] = []

    def __repr__(self):
        return f"({self.vid}, {self.zid})"

    def link_to(self, other: "TCG_Node", type: int):
        edge = TCG_Edge(type, self, other)
        self.outgoing.append(edge)
        return edge


class TCG_Edge:
    def __init__(self, type: int, start: "TCG_Node", end: "TCG_Node"):
        self.type = type
        self.start = start
        self.end = end

    def __repr__(self):
        return f"TCGE({self.type}, {self.start} → {self.end})"


class TCG:
    def __init__(self):
        self.vehicles: list[Vehicle] = []
        self.nodes: list[TCG_Node] = []
        self.edges: list[TCG_Edge] = []

        self.prev_vehicle = [None, None, None, None]
        self.zone_vehicles = [[], [], [], []]

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        start = TCG_Node(vehicle.id, vehicle.start)

        # handle type 1 edge
        curr = start
        self.nodes.append(curr)  # add start node
        self.zone_vehicles[vehicle.start].append(curr)
        for z in vehicle.path[1:]:
            end = TCG_Node(vehicle.id, z)
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
            for n1 in nodes:
                for n2 in nodes:
                    edge = n1.link_to(n2, 3)
                    self.edges.append(edge)
                    edge = n2.link_to(n1, 3)
                    self.edges.append(edge)

    def print_edges(self):
        print(*self.edges, sep="\n")


class RCG_Node:
    def __init__(self, vid: int, start: int, end: int):
        self.vid = vid
        self.start = start
        self.end = end
        self.outgoing: list["TCG_Edge"] = []

    def __repr__(self):
        return f"({self.vid}, {self.start}, {self.end})"

    def link_to(self, other: "RCG_Node"):
        RCG_edge = RCG_Edge(self, other)
        self.outgoing.append(RCG_edge)
        return RCG_edge


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

    def convert(self, TCG: TCG):
        for graph_edge in TCG.edges:
            # create the conflict graph node
            if graph_edge.type == 1:
                RCG_start = RCG_Node(graph_edge.start.vid, graph_edge.start.zid, graph_edge.end.zid)
                self.nodes.append(RCG_start)

        # create the resource conflict graph edge  according to the slide_6 p42 rule(a)
        for RCG_node_ind in range(len(self.nodes)):
            cur_id = self.nodes[RCG_node_ind].vid
            while (RCG_node_ind + 1 < len(self.nodes)) and self.nodes[RCG_node_ind + 1].vid == cur_id:
                RCG_edge = self.nodes[RCG_node_ind].link_to(self.nodes[RCG_node_ind + 1])
                RCG_node_ind = RCG_node_ind + 1
                self.edges.append(RCG_edge)
        # TODO: create the resource conflict graph edge according to the slide_6 p42 rule(b)~(e)


def main():
    tcg = TCG()

    # keep reading until eof
    for line in sys.stdin:
        tcg.add_vehicle(Vehicle(*map(int, line.split())))

    tcg.build_type_3_edge()

    # examples:
    # print(tcg.vehicles[0])
    # print(tcg.nodes[0])
    # print(*tcg.edges, sep="\n")
    # print all type 1 edge
    print(*[e for e in tcg.edges if e.type == 1], sep="\n")
    # print(len(tcg.edges))

    # TODO: build resource conflict graph
    rcg = RCG()
    rcg.convert(tcg)

    print("=== resource_conflict_graph_nodes ===")
    print(*rcg.nodes, sep="\n")

    print("=== resource_conflict_graph_edges ===")
    print(*rcg.edges, sep="\n")
    # TODO: solve


if __name__ == "__main__":
    main()
