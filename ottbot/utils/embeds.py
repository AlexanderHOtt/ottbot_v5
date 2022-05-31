# -*- coding=utf-8 -*-
"""Embed Factory."""
import datetime
import typing as t

import hikari

FieldsT = t.Optional[t.Iterable[tuple[t.Any, t.Any, bool]]]


class EmbedFactory:
    """Construct discord embeds."""

    @staticmethod
    def build(title: t.Any, desc: t.Any, url: str | None = None, color: hikari.Colorish | None = None) -> hikari.Embed:
        embed = hikari.Embed(title=title, description=desc, url=url, color=color, timestamp=datetime.datetime.now())
        return embed
