import heapq
from src.models import ZoneType


class Pathfinder:
    def __init__(self, graph):
        self.zones = graph.zones.values()
        self.cons = graph.connections
        self.graph = graph

    def dijkstra(self):
        open_list = []
        path = {zone: None for zone in self.zones}
        dist = {zone: float("inf") for zone in self.zones}
        loc = self.graph.get_zone(self.graph.start_hub)
        origin = loc
        counter = 0
        dist[origin] = 0
        heapq.heappush(open_list, (0, counter, origin))
        while open_list:
            d, _, z = heapq.heappop(open_list)
            if z == self.graph.get_zone(self.graph.end_hub):
                break
            if d > dist[z]:
                continue
            neighbors = self.graph.neighbors(z.name)
            for n in neighbors:
                neighbor = (self.graph.get_zone(n))
                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue
                new_dist = neighbor.get_cost() + d
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    path[neighbor] = z
                    counter += 1
                    heapq.heappush(open_list, (new_dist, counter, neighbor))
        return path

    def get_actual_path(self, path: dict) -> list:
        end_hub = self.graph.get_zone(self.graph.end_hub)
        start_hub = self.graph.get_zone(self.graph.start_hub)
        new = []
        curr = end_hub
        if end_hub not in path.keys():
            return None
        while curr != start_hub:
            new.append(curr)
            curr = path[curr]
        new.append(start_hub)
        new.reverse()
        return new
