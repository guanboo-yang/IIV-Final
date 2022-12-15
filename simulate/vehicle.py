import pygame
from pygame import sprite
from pygame.math import Vector2
from enum import Enum

from zone import Zone
from path import get_path
from utils import next_iter, gen_color

VEHICLE_RATIO = 0.08


class State(Enum):
    INIT = 0
    QUEUE = 1
    ZONE = 2
    EXIT = 3


# Create a subclass of the Sprite class
class Vehicle(sprite.Sprite):
    def __init__(self, id: int, start: int, end: int):
        super().__init__()
        self.id = id
        self.start = start
        self.end = end
        # enter state
        self.state = State.INIT

        # states: [(1, 0), (2, 1), (4, 2), (6, 3)]
        self.image = pygame.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.image.fill((255, 255, 255), self.rect)
        pygame.draw.rect(self.image, gen_color(), self.rect, 2)

        font = pygame.font.SysFont("menlo", 20)
        text = font.render(str(self.id), True, (0, 0, 0))
        text_rect = text.get_rect()
        setattr(text_rect, "center", self.rect.center)
        self.image.blit(text, text_rect)

        path = get_path(self.start, self.end)
        self.path = iter(path)
        self.release = lambda _: None

    def forward(self):
        if self.target == None:
            return
        # calculate distance
        diff = Vector2(self.target) - Vector2(self.center)
        # multiply by ratio
        diff *= VEHICLE_RATIO
        # set upper limit
        if diff.length() > 3:
            diff.scale_to_length(5)
        # get real center (float)
        self.center = self.center + diff
        # update approximate center (int)
        self.rect.center = self.center

    def distance(self, dest=None):
        # get next zone position
        if dest == None:
            dest = Vector2(self.target)
        # get current position
        pos = Vector2(self.rect.center)
        # return distance
        return (dest - pos).length()

    def update(self, time: float, zones: list[Zone]):
        # if self.id == 5:
        #     print(f"\r{self.state}", end="")
        if self.state == State.INIT:
            self.rect.center = zones[self.start].start
            self.center = Vector2(self.rect.center)
            self.dest = next_iter(self.path)
            self.target = zones[self.start].pos
            self.enter = False
            self.state = State.QUEUE
            return
        elif self.state == State.QUEUE:
            zone = zones[self.start]
            pos = Vector2(zone.queue) * (zone.vehicles.index(self) * 41 + 50)
            pos = pos + Vector2(zone.pos)
            self.target = pos
            self.forward()
            if zone.vehicles.index(self) == 0:
                self.target = zones[self.start].pos
                if self.distance() < 100 and zones[self.start].waiting == self.id:
                    self.enter = True
                    self.state = State.ZONE
            return
        elif self.dest == None:
            # release the zone
            self.release(time)
            self.release = lambda _: None
            self.target = zones[self.end].end
            # keep going to final zone
            self.forward()
        elif self.target == None:
            # new target position
            self.target = zones[self.dest].pos
        elif zones[self.dest].waiting == self.id:
            if self.enter:
                zones[self.start].vehicles.remove(self)
                self.enter = False
            # release the zone
            self.release(time)
            self.release = lambda _: None
            # keep going to dest zone
            self.forward()
        else:
            # wait for dest zone empty...
            pass
        if self.distance() < 2:
            if self.dest == self.end:
                self.state = State.EXIT
            # close enough
            if self.dest == None:
                # remove the vehicle
                self.kill()
                return
            # update the release funciotn, ready to release the zone
            self.release = zones[self.dest].release
            # update dest zone, waiting zone to be empty...
            self.dest = next_iter(self.path)
            if self.dest == self.end:
                self.state = State.EXIT
            self.target = None

    def __repr__(self):
        return f"{self.id}"


class Group(sprite.Group):
    def __init__(self, screen: pygame.Surface, zones: list[Zone], *sprites):
        super().__init__(*sprites)
        self.screen = screen
        self.zones = zones

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

    def sprites(self) -> list[Vehicle]:
        return super().sprites()

    def add(self, *vehicles: Vehicle):
        for vehicle in vehicles:
            self.zones[vehicle.start].vehicles.append(vehicle)
        super().add(*vehicles)
