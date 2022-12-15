import pygame

from utils import next_iter

WAIT_TILL_RELEASE = 180
TIME_OFFSET = -1

ZONES: list[dict[str, tuple[int, int]]] = [
    {"pos": (275, 275), "start": (275, 0), "end": (0, 275), "queue": (0, -1)},
    {"pos": (275, 325), "start": (0, 325), "end": (275, 600), "queue": (-1, 0)},
    {"pos": (325, 325), "start": (325, 600), "end": (600, 325), "queue": (0, 1)},
    {"pos": (325, 275), "start": (600, 275), "end": (325, 0), "queue": (1, 0)},
]


class Zone:
    def __init__(self, screen: pygame.Surface, id: int, vids: list[int] = [], size: int = 50):
        self.screen = screen
        self.id = id
        self.pos = ZONES[id]["pos"]
        self.start = ZONES[id]["start"]
        self.end = ZONES[id]["end"]
        self.queue = ZONES[id]["queue"]
        self.size = size
        self.vids = iter(vids)
        self.vehicles: list = []
        self.waiting = None
        self.release_time = 0
        self.finish = False

    def release(self, time: float):
        # record release time
        self.release_time = time
        # not wait for anyone
        self.waiting = None

    def update(self, screen: pygame.Surface, time: float):
        if self.waiting == None and time - self.release_time > WAIT_TILL_RELEASE / 1000:
            # wait next vehicle
            self.waiting = next_iter(self.vids)
            if self.waiting == None:
                self.finish = True
        self.draw(screen)

    def turn_on(self, color: tuple[int, int, int]):
        # brighter
        self.draw(self.screen, (191 + color[0] // 4, 191 + color[1] // 4, 191 + color[2] // 4))

    def draw(self, screen: pygame.Surface, bg: tuple[int, int, int] = (255, 255, 255)):
        pos = (self.pos[0] - self.size / 2 - 1, self.pos[1] - self.size / 2 - 1)
        pygame.draw.rect(screen, bg, pygame.Rect(pos, (self.size + 2, self.size + 2)))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(pos, (self.size + 2, self.size + 2)), 2)
        font = pygame.font.SysFont("menlo", 30, bold=True)
        text_surface = font.render(str(self.id), True, (180, 180, 180))
        text_rect = text_surface.get_rect()
        setattr(text_rect, "center", self.pos)
        screen.blit(text_surface, text_rect)

    def __repr__(self):
        return f"[{self.id}: {self.finish}]"


class Zones:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("menlo", 30, bold=True)
        self.time = TIME_OFFSET
        self.running = True
        self.pause = False

    def draw_text(self, text: str, pos: tuple[int, int], color: tuple[int, int, int] = (0, 0, 0), align: str = "center"):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        setattr(text_rect, align, pos)
        self.screen.blit(text_surface, text_rect)

    def draw_line(self, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int] = (0, 0, 0)):
        start = (start[0] - 1, start[1] - 1)
        end = (end[0] - 1, end[1] - 1)
        pygame.draw.line(self.screen, color, start, end, 2)

    def draw_background(self):
        self.draw_line((0, 250), (250, 250))
        self.draw_line((350, 250), (600, 250))
        self.draw_line((0, 300), (250, 300))
        self.draw_line((350, 300), (600, 300))
        self.draw_line((0, 350), (250, 350))
        self.draw_line((350, 350), (600, 350))
        self.draw_line((250, 0), (250, 250))
        self.draw_line((250, 350), (250, 600))
        self.draw_line((300, 0), (300, 250))
        self.draw_line((300, 350), (300, 600))
        self.draw_line((350, 0), (350, 250))
        self.draw_line((350, 350), (350, 600))
        self.draw_text(f"{self.time:.1f}", (585, 585), align="bottomright")

    def update(self, time: float, pause: bool):
        ...

    def run(self):
        try:
            while self.running:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if not self.pause:
                    self.time += self.clock.tick(60) / 1000
                else:
                    self.clock.tick(60)
                self.screen.fill((255, 255, 255))
                self.draw_background()
                self.update(self.time, self.pause)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.pause = not self.pause
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.pause = not self.pause
        except KeyboardInterrupt:
            print("\n\rGoodbye!")
        finally:
            pygame.quit()
