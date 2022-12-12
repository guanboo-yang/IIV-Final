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

class Resource_Conflict_Graph_Node:
    def __init__(self, vid: int, start: int, end: int):
        self.vid = vid
        self.start = start
        self.end = end
        self.outgoing: list["Edge"] = []

    def __repr__(self):
        return f"Resource_Conflict_Graph_Node ({self.vid}, {self.start}, {self.end})"

    def link_to(self, other: "Resource_Conflict_Graph_Node", type: int):
        RCG_edge = Resource_Conflict_Graph_Edge(type, self, other)
        self.outgoing.append(RCG_edge)
        return RCG_edge
    

class Resource_Conflict_Graph_Edge:
    def __init__(self, start: "Resource_Conflict_Graph_Node", end: "Resource_Conflict_Graph_Node"):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Resource_Conflict_Graph_Edge ({self.type}, {self.start} → {self.end})"

class Resource_Conflict_Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def convert(self, Graph:Graph):
        
        for graph_edge in Graph.edges:  
            
            # create the resource conflict graph node
            if graph_edge.type == 1:

                RCG_start = Resource_Conflict_Graph_Node(graph_edge.start.vid, graph_edge.start.zid, graph_edge.end.zid)
                
                self.nodes.append(RCG_start)
                
        #TODO: create the resource conflict graph edge according to the rule from slide 6 p42
            
        


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
    resource_conflict_graph = Resource_Conflict_Graph()
    resource_conflict_graph.convert(graph)
    print(*resource_conflict_graph.nodes, sep="\n")
    # TODO: solve


if __name__ == "__main__":
    main()
