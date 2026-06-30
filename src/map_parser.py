from __future__ import annotations
from typing import Optional
from src.models import Connection, Graph, Zone, ZoneType


class ParseError(Exception):
    """Raised when the input file violates the expected format."""
    def __init__(self, lineno: int, message: str) -> None:
        """Store line number and human-readable cause."""
        prefix = f"Line {lineno}: " if lineno > 0 else ""
        super().__init__(f"{prefix}{message}")
        self.lineno = lineno
        self.message = message


class Parser:
    """Parses a drone map file line by line and builds a Graph.
    One instance = one parse run. Do not reuse across files.
    """

    def __init__(self) -> None:
        """Initialise empty parser state."""
        self.nb_drones: Optional[int] = None
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.seen_connections: set[frozenset[str]] = set()
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None

    def parse_file(self, filepath: str) -> Graph:
        """Parse *filepath* and return a validated Graph.

        Raises ParseError on any structural or semantic error.
        Raises OSError / FileNotFoundError if the file cannot be opened.
        """
        with open(filepath) as f:
            lines = f.readlines()
        first_real_line = True
        for lineno, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if first_real_line:
                if not line.startswith('nb_drones:'):
                    raise ParseError(
                        lineno,
                        "first line must be 'nb_drones: <positive_integer>'"
                    )
                self.parse_nb_drones(line, lineno)
                first_real_line = False
                continue
            if line.startswith('nb_drones:'):
                raise ParseError(
                    lineno, "'nb_drones' must appear exactly once"
                )
            elif line.startswith('start_hub:'):
                self.parse_zone(line, lineno, is_start=True)
            elif line.startswith('end_hub:'):
                self.parse_zone(line, lineno, is_end=True)
            elif line.startswith('hub:'):
                self.parse_zone(line, lineno)
            elif line.startswith('connection:'):
                self.parse_connection(line, lineno)
            else:
                prefix = (
                    line.split(':')[0] if ':' in line else line.split()[0]
                )
                raise ParseError(lineno, f"unknown line type '{prefix}'")
        self.validate_global()
        assert self.nb_drones is not None
        assert self.start_hub is not None
        assert self.end_hub is not None
        return Graph(
            nb_drones=self.nb_drones,
            start_hub=self.start_hub,
            end_hub=self.end_hub,
            zones=self.zones,
            connections=self.connections,
        )

    def parse_nb_drones(self, line: str, lineno: int) -> None:
        """Parse the nb_drones line and store the value."""
        _, _, raw = line.partition(':')
        value = raw.strip()
        if not value:
            raise ParseError(lineno, "'nb_drones' missing value")
        if not self.is_int(value):
            raise ParseError(
                lineno,
                f"'nb_drones' must be a positive integer, got '{value}'"
            )
        n = int(value)
        if n <= 0:
            raise ParseError(
                lineno,
                f"'nb_drones' must be a positive integer, got {n}"
            )
        self.nb_drones = n

    def parse_zone(self, line: str, lineno: int,
                   is_start: bool = False, is_end: bool = False) -> None:
        """Parse a hub / start_hub / end_hub line and register the zone."""
        _, _, rest = line.partition(':')
        rest = rest.strip()
        rest, meta_str = self.extract_meta(rest, lineno)
        tokens = rest.split()
        if len(tokens) != 3:
            raise ParseError(
                lineno,
                f"zone expects name x y, got {len(tokens)} token(s)"
            )
        name, x_str, y_str = tokens
        if not name:
            raise ParseError(lineno, "zone name must not be empty")
        if '-' in name:
            raise ParseError(
                lineno,
                f"zone name '{name}' must not contain dashes "
                "(dashes are reserved for the connection syntax)"
            )
        if not self.is_int(x_str):
            raise ParseError(
                lineno, f"x coordinate must be an integer, got '{x_str}'"
            )
        if not self.is_int(y_str):
            raise ParseError(
                lineno, f"y coordinate must be an integer, got '{y_str}'"
            )
        for z in self.zones.values():
            c = (int(x_str), int(y_str))
            if c == (z.x, z.y):
                raise ParseError(lineno, f"multiple zones on coordinates {c}")
        if name in self.zones:
            raise ParseError(lineno, f"duplicate zone name '{name}'")
        if is_start:
            if self.start_hub is not None:
                raise ParseError(lineno, "multiple 'start_hub' definitions")
            self.start_hub = name
        if is_end:
            if self.end_hub is not None:
                raise ParseError(lineno, "multiple 'end_hub' definitions")
            self.end_hub = name
        zone_type = ZoneType.NORMAL
        color: str = "yellow"
        max_drones = 1
        if meta_str is not None:
            zone_type, color, max_drones = (
                self.parse_zone_meta(meta_str, lineno)
            )
        self.zones[name] = Zone(
            name=name,
            x=int(x_str),
            y=int(y_str),
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            is_start=is_start,
            is_end=is_end,
        )

    def parse_zone_meta(self, meta_str: str,
                        lineno: int) -> tuple[ZoneType, str, int]:
        """Return (zone_type, color, max_drones) from bracket content."""
        zone_type = ZoneType.NORMAL
        color: str = "yellow"
        max_drones = 1
        seen: set[str] = set()
        for pair in meta_str.split():
            key, sep, value = pair.partition('=')
            if not sep:
                raise ParseError(
                    lineno,
                    f"invalid metadata '{pair}', expected 'key=value'"
                )
            if not key:
                raise ParseError(lineno, "metadata key is empty")
            if not value:
                raise ParseError(
                    lineno, f"metadata key '{key}' has no value"
                )
            if key in seen:
                raise ParseError(
                    lineno, f"duplicate metadata key '{key}'"
                )
            seen.add(key)
            if key == 'zone':
                try:
                    zone_type = ZoneType(value)
                except ValueError:
                    valid = ', '.join(t.value for t in ZoneType)
                    raise ParseError(
                        lineno,
                        f"invalid zone type '{value}', must be: {valid}"
                    )
            elif key == 'color':
                color = value
            elif key == 'max_drones':
                if not self.is_int(value) or int(value) <= 0:
                    raise ParseError(
                        lineno,
                        "'max_drones' must be a positive"
                        f" integer, got '{value}'"
                    )
                max_drones = int(value)
            else:
                raise ParseError(
                    lineno, f"unknown zone metadata key '{key}'"
                )
        return zone_type, color, max_drones

    def parse_connection(self, line: str, lineno: int) -> None:
        """Parse a connection line and register the edge."""
        _, _, rest = line.partition(':')
        rest = rest.strip()
        rest, meta_str = self.extract_meta(rest, lineno)
        tokens = rest.split()
        if len(tokens) == 0:
            raise ParseError(lineno, "connection is missing 'zone1-zone2'")
        if len(tokens) > 1:
            raise ParseError(
                lineno,
                f"connection expects 'zone1-zone2' (use '-' not space),"
                f" got {len(tokens)} word(s): {tokens}"
            )
        pair = tokens[0]
        dash_count = pair.count('-')
        if dash_count == 0:
            raise ParseError(
                lineno, f"connection '{pair}' must contain a '-' separator"
            )
        if dash_count > 1:
            raise ParseError(
                lineno,
                f"connection '{pair}' has {dash_count} dashes"
                " — zone names cannot contain dashes"
            )
        zone1, _, zone2 = pair.partition('-')
        if not zone1:
            raise ParseError(lineno, "connection has empty first zone name")
        if not zone2:
            raise ParseError(lineno, "connection has empty second zone name")
        if zone1 not in self.zones:
            raise ParseError(lineno, f"zone '{zone1}' is not defined")
        if zone2 not in self.zones:
            raise ParseError(lineno, f"zone '{zone2}' is not defined")
        if zone1 == zone2:
            raise ParseError(
                lineno,
                f"self-connection: '{zone1}' cannot connect to itself"
            )
        key: frozenset[str] = frozenset({zone1, zone2})
        if key in self.seen_connections:
            raise ParseError(
                lineno,
                f"duplicate connection between '{zone1}' and '{zone2}'"
            )
        self.seen_connections.add(key)
        max_link_capacity = 1
        if meta_str is not None:
            max_link_capacity = self.parse_connection_meta(meta_str, lineno)
        self.connections.append(Connection(
            zone1=zone1,
            zone2=zone2,
            max_link_capacity=max_link_capacity,
        ))

    def parse_connection_meta(self, meta_str: str, lineno: int) -> int:
        """Return max_link_capacity parsed from bracket content."""
        max_link_capacity = 1
        seen: set[str] = set()
        for pair in meta_str.split():
            key, sep, value = pair.partition('=')
            if not sep:
                raise ParseError(
                    lineno,
                    f"invalid metadata '{pair}', expected 'key=value'"
                )
            if not key:
                raise ParseError(lineno, "metadata key is empty")
            if not value:
                raise ParseError(
                    lineno, f"metadata key '{key}' has no value"
                )
            if key in seen:
                raise ParseError(
                    lineno, f"duplicate metadata key '{key}'"
                )
            seen.add(key)
            if key == 'max_link_capacity':
                if not self.is_int(value) or int(value) <= 0:
                    raise ParseError(
                        lineno,
                        "'max_link_capacity' must be a positive"
                        f" integer, got '{value}'"
                    )
                max_link_capacity = int(value)
            else:
                raise ParseError(
                    lineno, f"unknown connection metadata key '{key}'"
                )
        return max_link_capacity

    def extract_meta(self, rest: str,
                     lineno: int) -> tuple[str, Optional[str]]:
        """Split 'tokens [meta content]' into ('tokens', 'meta content').

        Returns (rest, None) when no brackets are present.
        """
        has_open = '[' in rest
        has_close = ']' in rest
        if not has_open and not has_close:
            return rest, None
        if has_close and not has_open:
            raise ParseError(lineno, "closing ']' without opening '['")
        if has_open and not has_close:
            raise ParseError(lineno, "opening '[' without closing ']'")
        if rest.count('[') > 1:
            raise ParseError(lineno, "multiple '[' on one line")
        if rest.count(']') > 1:
            raise ParseError(lineno, "multiple ']' on one line")
        open_idx = rest.index('[')
        close_idx = rest.index(']')
        if close_idx < open_idx:
            raise ParseError(lineno, "']' appears before '['")
        after = rest[close_idx + 1:].strip()
        if after:
            raise ParseError(
                lineno, f"unexpected content after ']': '{after}'"
            )
        meta_content = rest[open_idx + 1:close_idx]
        before = rest[:open_idx].strip()
        return before, meta_content

    def validate_global(self) -> None:
        """Validate constraints that require the complete parse."""
        if self.nb_drones is None:
            raise ParseError(0, "file is empty or missing 'nb_drones'")
        if self.start_hub is None:
            raise ParseError(0, "missing 'start_hub' definition")
        if self.end_hub is None:
            raise ParseError(0, "missing 'end_hub' definition")
        if self.start_hub == self.end_hub:
            raise ParseError(
                0, "start_hub and end_hub must be different zones"
            )

    @staticmethod
    def is_int(s: str) -> bool:
        """Return True if *s* is a valid integer (including negative)."""
        try:
            int(s)
            return True
        except ValueError:
            return False
