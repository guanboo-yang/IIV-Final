import sys
from path import get_path

from vehicle import Vehicle, Group
from zone import Zones, Zone


class MyGame(Zones):
    def __init__(self):
        super().__init__()
        self.zones: list[Zone] = []
        self.group = Group(self.screen, self.zones)
        self.vehicles: dict[int, list[Vehicle]] = {}

    def update(self, time: float, pause: bool):
        for zone in self.zones:
            zone.update(self.screen, self.time)
        self.group.update(time, self.zones, pause)
        self.group.draw(self.screen)
        to_add = []
        for arri in self.vehicles:
            if time > arri:
                to_add.append(arri)
        for arri in to_add:
            self.group.add(*self.vehicles[arri])
            self.vehicles.pop(arri)

        # print(f"\r{self.zones}", end="")
        if all([zone.finish for zone in self.zones]):
            self.pause = True

    def add_vehicle(self, arri: int, vehicle: Vehicle):
        if arri in self.vehicles:
            self.vehicles[arri].append(vehicle)
        else:
            self.vehicles[arri] = [vehicle]

    def load(self, file1: str, file2: str = None):
        zones = [[] for _ in range(4)]
        with open(file1) as f:
            print("Loading testcase:", file1)
            for line in f:
                id, arri, start, end = map(int, line.split())
                self.add_vehicle(arri, Vehicle(id, start, end))
                for zone in get_path(start, end):
                    zones[zone].append(id)
        if file2 == None:
            print("No schedule file provided, using FCFS schedule")
            for idx, zone in enumerate(zones):
                self.zones.append(Zone(self.screen, idx, zone))
            return
        with open(file2) as f:
            print("Loading schedule:", file2)
            for idx, line in enumerate(f):
                self.zones.append(Zone(self.screen, idx, list(map(int, line.split()))))


if __name__ == "__main__":
    game = MyGame()
    args = sys.argv[1:]
    if len(args) == 1:
        game.load(args[0])
    elif len(args) == 2:
        game.load(args[0], args[1])
    else:
        exit("Usage: python simulate <testcase> <schedule>")
    game.run()
