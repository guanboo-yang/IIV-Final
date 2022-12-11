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


class Node:
    def __init__(self, vid: int, zid: int):
        self.vid = vid
        self.zid = zid
        self.outgoing: list["Edge"] = []

    def __repr__(self):
        return f"({self.vid}, {self.zid})"

    def link_to(self, other: "Node", type: int):
        edge = Edge(type, self, other)
        self.outgoing.append(edge)
        return edge


class Edge:
    def __init__(self, type: int, start: "Node", end: "Node"):
        self.type = type
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Edge({self.type}, {self.start} → {self.end})"


class Graph:
    def __init__(self):
        self.vehicles: list[Vehicle] = []
        self.nodes: list[Node] = []

        self.edges = []

        self.prev_vehicle = [None, None, None, None]
        self.zone_vehicles = [[], [], [], []]

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        start = Node(vehicle.id, vehicle.start)

        # handle type 1 edge
        curr = start
        self.nodes.append(curr)  # add start node
        self.zone_vehicles[vehicle.start].append(curr)
        for z in vehicle.path[1:]:
            end = Node(vehicle.id, z)
            edge = curr.link_to(end, 1)
            self.edges.append(edge)
            curr = end
            self.zone_vehicles[z].append(curr)

        # hadle type 2 edge
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


def main():
    graph = Graph()

    # keep reading until eof
    for line in sys.stdin:
        graph.add_vehicle(Vehicle(*map(int, line.split())))

    graph.build_type_3_edge()

    # examples:
    # print(graph.vehicles[0])
    # print(graph.nodes[0])
    # print(graph.nodes[0].outgoing)
    # print(graph.nodes[0].outgoing[0].end)
    # print(graph.nodes[0].outgoing[0].end.outgoing)
    print(*graph.edges, sep="\n")
    print(len(graph.edges))

    # TODO: build resource conflict graph
    # TODO: solve


if __name__ == "__main__":
    main()
