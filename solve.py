class Vehicle:
    def __init__(self, vehicle_id, arrive_time, start, end, payment):
        self.vehicle_id = vehicle_id
        self.arrive_time = arrive_time
        self.start = start
        self.end = end
        self.payment = payment

        self.path = [start]
        while start != end:
            start = (start + 1) % 4
            self.path.append(start)

    def __repr__(self):
        return f"Vehicle({self.vehicle_id}, {' → '.join(map(str, self.path))})"


class Node:
    def __init__(self, vid: int, zid: int):
        self.vid = vid
        self.zid = zid
        self.outgoing: list["Edge"] = []

    def __repr__(self):
        return f"({self.vid}, {self.zid})"

    def link_to(self, other: "Node"):
        self.outgoing.append(Edge(1, self, other))


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

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        start = Node(vehicle.vehicle_id, vehicle.start)

        # handle type 1 edge
        curr = start
        self.nodes.append(curr)  # add start node
        for i in vehicle.path[1:]:
            end = Node(vehicle.vehicle_id, i)
            curr.link_to(end)
            curr = end


def main():
    graph = Graph()

    n = int(input())

    for _ in range(n):
        graph.add_vehicle(Vehicle(*map(int, input().split())))

    # solve
    print(graph.vehicles[0])
    print(graph.vehicles[1])
    print(graph.nodes[0])
    print(graph.nodes[0].outgoing)
    print(graph.nodes[0].outgoing[0].end)
    print(graph.nodes[0].outgoing[0].end.outgoing)


if __name__ == "__main__":
    main()
