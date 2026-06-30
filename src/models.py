from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ZoneType(Enum):
    """Movement cost and routing behaviour of a zone."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    """A node in the drone network graph."""

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: str = "yellow"
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    def __hash__(self) -> int:
        return hash(self.name)

    def get_cost(self) -> int:
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        elif self.zone_type == ZoneType.NORMAL:
            return 1
        return 0


@dataclass
class Connection:
    """A bidirectional edge between two zones."""

    zone1: str
    zone2: str
    max_link_capacity: int = 1

    def other(self, name: str) -> str:
        """Return the zone on the opposite side of this connection."""
        return self.zone2 if name == self.zone1 else self.zone1

    def involves(self, name: str) -> bool:
        """Return True if this connection touches the named zone."""
        return name in (self.zone1, self.zone2)


@dataclass
class Graph:
    """The fully parsed drone routing graph."""

    nb_drones: int
    start_hub: str
    end_hub: str
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)

    def neighbors(self, zone: str) -> list[str]:
        """Return the list of neighbors for a zone."""
        res = []
        for con in self.connections:
            if con.involves(zone):
                res.append(con.other(zone))
        return res

    def get_zone(self, zone: str) -> Zone:
        return self.zones[zone]

    def is_zone_blocked(self, zone: str) -> bool:
        """Return True if zone is blocked, False otherwise."""
        return self.zones[zone].zone_type == ZoneType.BLOCKED
