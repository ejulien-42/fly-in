from enum import Enum


class Color(Enum):
    """Enumeration for color, map string with RGB value"""
    BLACK = ("black", (0, 0, 0))
    WHITE = ("white", (255, 255, 255))
    RED = ("red", (255, 0, 0))
    GREEN = ("green", (0, 255, 0))
    BLUE = ("blue", (0, 0, 255))
    YELLOW = ("yellow", (255, 255, 0))
    ORANGE = ("orange", (255, 165, 0))
    CYAN = ("cyan", (0, 255, 255))
    MAGENTA = ("magenta", (255, 0, 255))
    PURPLE = ("purple", (128, 0, 128))
    PINK = ("pink", (255, 192, 203))
    GRAY = ("gray", (128, 128, 128))
    MAROON = ("maroon", (128, 0, 0))
    BROWN = ("brown", (165, 42, 42))
    GOLD = ("gold", (255, 215, 0))
    DARKRED = ("darkred", (139, 0, 0))
    VIOLET = ("violet", (238, 130, 238))
    CRIMSON = ("crimson", (220, 20, 60))
    RAINBOW = ("rainbow", (0, 0, 0))
    LIME = ("lime", (170, 255, 0))

    @classmethod
    def get_color(cls, color: str) -> tuple[int, int, int]:
        for col in cls:
            if col.value[0] == color:
                return col.value[1]
        return cls.BLACK.value[1]
