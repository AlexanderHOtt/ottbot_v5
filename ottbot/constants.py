# -*- coding=utf-8 -*-
"""Global constants."""
import typing as t

from hikari.colors import Color

MODULE_PATH = "ottbot/modules/"

DELETE_CUSTOM_ID: str = "AUTHOR_DELETE_BUTTON:"

ZWJ: t.Final[str] = "\u200d"


class Colors:
    """Predefined colors."""

    DEFAULT: t.Final[Color] = Color.from_hex_code("#713dc7")
    """Default color."""
    INFO: t.Final[Color] = Color.from_hex_code("#55CDFC")  # #55CDFC
    """Color used to represent an informational message."""
    OK: t.Final[Color] = Color.from_hex_code("#43B581")  # #43d439
    """Color used to represent a successful execution/attempt."""
    WARN: t.Final[Color] = Color.from_hex_code("#F7CA00")
    """Color used to represent a partially failed execution/attempt."""
    ERROR: t.Final[Color] = Color.from_hex_code("#ff0000")  # #F04747
    """Color used to represent a failed execution/attempt."""

    WHITE: t.Final[Color] = Color.from_hex_code("#FFFFFE")  # 0xFFFFFF is treated as no colour in embeds by Discord.
    """White color."""
