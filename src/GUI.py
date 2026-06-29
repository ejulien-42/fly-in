import pygame
from src.color import Color
from src.models import Zone


class GUI:
    def __init__(self, graph):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1000, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("ejulien's fly-in")
        self.graph = graph
        self.cons = self.graph.connections
        self.zones: list[Zone] = []
        self.zone_names: list[str] = []
        self.concerned_zones: list[str] = []
        self.concerned_cons: list[str] = []
        self.scaled_cos = {}
        self.size = (self.HEIGHT + self.WIDTH) / 100
        self.rad = self.size / 2
        self.selected = None
        self.info = ""
        self.turn_id = 0
        self.nb_turns = 0

    def run(self, turns):
        self.nb_turns = len(turns)
        start = self.graph.start_hub
        initial = [f"D{i}-{start}"
                   for i in range(1, self.graph.nb_drones + 1)]
        turns = [initial] + turns
        self.turns = turns
        self.last_turn = len(turns) - 1
        running = True
        self.get_coordinates()
        for zone in self.zones:
            self.zone_names.append(zone.name)
        self.update_drones()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.turn_id = self.last_turn
                        self.update_drones()
                    if event.key == pygame.K_RIGHT:
                        if self.turn_id == self.last_turn:
                            continue
                        else:
                            self.turn_id += 1
                            self.update_drones()
                    if event.key == pygame.K_LEFT:
                        if self.turn_id == 0:
                            continue
                        else:
                            self.turn_id -= 1
                            self.update_drones()
                    if event.key == pygame.K_DOWN:
                        self.turn_id = 0
                        self.update_drones()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for zone in self.zones:
                        x, y = self.scaled_cos[zone.name]
                        if x + self.rad > pos[0] and x - self.rad < pos[0]:
                            if y + self.rad > pos[1] and y - self.rad < pos[1]:
                                self.selected = zone
                                break
                        self.selected = None
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            self.screen.fill((255, 255, 255))
            self.draw_connections()
            self.draw_hubs()
            self.draw_drones()
            self.draw_nb_turns()
            if self.selected is not None:
                self.zone_info()
                font = pygame.font.SysFont("arial", 18)
                txt = font.render(self.info, True, (0, 0, 0))
                self.screen.blit(txt, (self.WIDTH * 0.05, self.HEIGHT * 0.95))
            pygame.display.flip()

    def is_connection(self, string: str) -> bool:
        i = 0
        for char in string:
            if char == "-":
                i += 1
        if i == 2:
            return True
        return False

    def update_drones(self):
        turn = self.turns[self.turn_id]
        print(f"\nTurn number: {self.turn_id}")
        print(turn)
        self.concerned_zones = []
        self.concerned_cons = []
        for action in turn:
            for zone in self.zone_names:
                if zone in action and not (self.is_connection(action)):
                    self.concerned_zones.append(zone)
        for action in turn:
            for con in self.cons:
                if con.zone1 in action and con.zone2 in action:
                    self.concerned_cons.append(con)

    def zone_info(self):
        info = {}
        info["color"] = self.selected.color
        info["coordinates"] = (self.selected.x, self.selected.y)
        info["name"] = self.selected.name
        info["type"] = self.selected.zone_type
        info["max_drones"] = self.selected.max_drones
        txt = f"Zone: {info['name']},  "
        txt += f"Coordinates: {info['coordinates']},  "
        txt += f"Color: {info['color']},  "
        txt += f"Zone type: {info['type'].value},  "
        txt += f"Max drones: {info['max_drones']}"
        self.info = txt

    def draw_nb_turns(self):
        font = pygame.font.SysFont("arial", 24)
        txt = font.render(f"{self.turn_id}/{self.nb_turns} turns",
                          True, (0, 0, 0))
        self.screen.blit(txt, (self.WIDTH * 0.85, self.HEIGHT * 0.02))

    def draw_drones(self):
        image = pygame.image.load("drone.png").convert_alpha()
        rad = self.rad
        for zone in self.zones:
            if zone.name in self.concerned_zones:
                image = pygame.transform.scale(image,
                                               (self.size * 1.5,
                                                self.size * 1.5))
                self.screen.blit(image,
                                 (self.scaled_cos[zone.name][0] - rad * 1.5,
                                  self.scaled_cos[zone.name][1] - rad * 1.5))
        for con in self.concerned_cons:
            z1 = con.zone1
            z2 = con.zone2
            x1 = self.scaled_cos[z1][0]
            x2 = self.scaled_cos[z2][0]
            y1 = self.scaled_cos[z1][1]
            y2 = self.scaled_cos[z2][1]
            final_x = (x1 + x2) / 2
            final_y = (y1 + y2) / 2
            image = pygame.transform.scale(image,
                                           (self.size * 1.5, self.size * 1.5))
            self.screen.blit(image, (final_x - rad * 1.5, final_y - rad * 1.5))

    def draw_hubs(self):
        for zone in self.zones:
            pygame.draw.circle(self.screen, Color.get_color(zone.color),
                               self.scaled_cos[zone.name], self.size)

    def draw_connections(self):
        for con in self.graph.connections:
            z1 = con.zone1
            z2 = con.zone2
            x1 = self.scaled_cos[z1][0]
            x2 = self.scaled_cos[z2][0]
            y1 = self.scaled_cos[z1][1]
            y2 = self.scaled_cos[z2][1]
            pygame.draw.line(self.screen, (0, 0, 0),
                             (x1, y1), (x2, y2), 1)

    def get_coordinates(self):
        all_x = []
        all_y = []
        for zone in self.graph.zones:
            all_x.append(self.graph.get_zone(zone).x)
            all_y.append(self.graph.get_zone(zone).y)
            self.zones.append(self.graph.get_zone(zone))
        max_x = max(all_x)
        min_x = min(all_x)
        max_y = max(all_y)
        min_y = min(all_y)
        real_width = 0.8 * self.WIDTH
        real_height = 0.8 * self.HEIGHT
        range_x = max_x - min_x
        range_y = max_y - min_y
        for zone in self.zones:
            if range_x == 0:
                x_scaled = real_width / 2
            else:
                x_scaled = (real_width / range_x) * (zone.x - min_x)
            if range_y == 0:
                y_scaled = real_height / 2
            else:
                y_scaled = (real_height / range_y) * (zone.y - min_y)
            x_scaled += self.WIDTH * 0.1
            y_scaled += self.HEIGHT * 0.1
            if y_scaled > self.HEIGHT / 2:
                d = y_scaled - self.HEIGHT / 2
                y_scaled = self.HEIGHT / 2 - d
            elif y_scaled < self.HEIGHT / 2:
                d = self.HEIGHT / 2 - y_scaled
                y_scaled = self.HEIGHT / 2 + d
            self.scaled_cos[zone.name] = (x_scaled, y_scaled)
