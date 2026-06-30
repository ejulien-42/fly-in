from typing import Optional
from src.models import ZoneType, Graph, Zone, Connection


class Simulation:
    """
    Simulation class, will be used to simulate each
    turn necessary for map completion.
    """
    def __init__(self, path: list[Zone], graph: Graph) -> None:
        """Constructor for the simulation class."""
        self.path = path
        self.graph = graph
        self.nb_drones = self.graph.nb_drones

    def simulate(self) -> list[list[str]]:
        """
        Main method of the class. Returns all the
        turns necessary for map completion
        """
        path = self.path
        end_idx = len(path) - 1
        idx = {i: 0 for i in range(1, self.nb_drones + 1)}
        remaining = {i: 0 for i in range(1, self.nb_drones + 1)}
        turns: list[list[str]] = []
        while not all(idx[i] == end_idx
                      for i in range(1, self.nb_drones + 1)):
            zone_occupancy: dict[Zone, int] = {}
            link_usage: dict[frozenset[str], int] = {}
            for i in range(1, self.nb_drones + 1):
                if remaining[i] > 0:
                    dst = path[idx[i] + 1]
                    zone_occupancy[dst] = zone_occupancy.get(dst, 0) + 1
                    link = frozenset([path[idx[i]].name, dst.name])
                    link_usage[link] = link_usage.get(link, 0) + 1
                else:
                    z = path[idx[i]]
                    zone_occupancy[z] = zone_occupancy.get(z, 0) + 1
            turn = []
            for drone_id in range(1, self.nb_drones + 1):
                cur = idx[drone_id]
                if remaining[drone_id] > 0:
                    remaining[drone_id] -= 1
                    next_zone = path[cur + 1]
                    if remaining[drone_id] == 0:
                        idx[drone_id] = cur + 1
                        turn.append(f"D{drone_id}-{next_zone.name}")
                    else:
                        turn.append(
                            f"D{drone_id}-{path[cur].name}-{next_zone.name}")
                    continue
                if cur == end_idx:
                    turn.append(f"D{drone_id}-{path[cur].name}")
                    continue
                next_zone = path[cur + 1]
                link = frozenset([path[cur].name, next_zone.name])
                conn = self._get_connection(path[cur].name, next_zone.name)
                assert conn is not None
                is_terminal = next_zone.name in (self.graph.start_hub,
                                                 self.graph.end_hub)
                zone_full = (not is_terminal
                             and zone_occupancy.get(next_zone, 0)
                             >= next_zone.max_drones)
                link_full = link_usage.get(link, 0) >= conn.max_link_capacity
                if zone_full or link_full:
                    turn.append(f"D{drone_id}-{path[cur].name}")
                    continue
                zone_occupancy[path[cur]] -= 1
                zone_occupancy[next_zone] = (
                    zone_occupancy.get(next_zone, 0) + 1)
                link_usage[link] = link_usage.get(link, 0) + 1
                if next_zone.zone_type == ZoneType.RESTRICTED:
                    remaining[drone_id] = 1
                    turn.append(
                        f"D{drone_id}-{path[cur].name}-{next_zone.name}")
                else:
                    idx[drone_id] = cur + 1
                    turn.append(f"D{drone_id}-{next_zone.name}")
            turns.append(turn)
        return turns

    def _get_connection(self, z1: str, z2: str) -> Optional[Connection]:
        """
        Utility method to get the connection between
        2 zones using their name as parameter.
        """
        for c in self.graph.connections:
            if c.involves(z1) and c.involves(z2):
                return c
        return None
