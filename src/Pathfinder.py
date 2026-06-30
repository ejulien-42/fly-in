import heapq
from typing import Optional
from src.models import ZoneType, Zone, Graph


class Pathfinder:
    """Th main algorithm class"""
    def __init__(self, graph: Graph):
        """Constructor for the pathfinder class."""
        self.zones = graph.zones.values()
        self.cons = graph.connections
        self.graph = graph

    def dijkstra(self) -> dict[Zone, Optional[Zone]]:
        """Main dijkstra algorithm."""
        open_list: list[tuple[float, int, Zone]] = []
        path: dict[Zone, Optional[Zone]] = {
            zone: None for zone in self.zones}
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

    def get_actual_path(self,
                        path: dict[Zone,
                                   Optional[Zone]]) -> list[Zone] | None:
        """Gets the path to a list of zones, in the right order."""
        end_hub = self.graph.get_zone(self.graph.end_hub)
        start_hub = self.graph.get_zone(self.graph.start_hub)
        new: list[Zone] = []
        curr = end_hub
        if path[end_hub] is None:
            return None
        while curr != start_hub:
            new.append(curr)
            parent = path[curr]
            assert parent is not None
            curr = parent
        new.append(start_hub)
        new.reverse()
        return new
