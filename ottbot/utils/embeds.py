# -*- coding=utf-8 -*-
"""Embed Factory."""
import datetime
import typing as t

import hikari
import tanjun

from ottbot.constants import Colors

FieldsT = t.Iterable[tuple[t.Any, t.Any, bool]] | None
"""Embed field type."""
ResourceishOrNoneT = hikari.Resourceish | None
"""Resourceish type."""
ESCAPE_NAME: t.Final[str] = "None"
"""Escape name for not including part of an embed."""


class EmbedFactory:
    """Construct discord embeds."""

    @staticmethod
    def build(
        ctx_or_event: tanjun.abc.Context | hikari.Event,
        bot: hikari.GatewayBot,
        /,
        *,
        title: t.Any = None,
        desc: t.Any = None,
        url: str | None = None,
        color: hikari.Colorish | None = None,
        fields: FieldsT | None = None,
        author: hikari.User | None = None,
        header: str | None = None,
        header_url: str | None = None,
        header_icon: ResourceishOrNoneT = None,
        footer: str | None = None,
        footer_icon: ResourceishOrNoneT = None,
        image: ResourceishOrNoneT | None = None,
        timestamp: datetime.datetime | None = None,
        thumbnail: ResourceishOrNoneT = None,
    ) -> hikari.Embed:
        r"""Construct an embed.

        ╭─────────────────────────────────────────────────────────────────────╮
        │ ╭──────╮                                             ╭───────────╮  │
        │ │Header│     Header (linked to url)                  │           │  │
        │ │ Icon │     ‾‾‾‾‾‾                                  │ Thumbnail │  │
        │ ╰──────╯                                             │           │  │
        │                                                      │           │  │
        │  EMBED TITLE                                         ╰───────────╯  │
        │  ‾‾‾‾‾‾‾‾‾‾‾                                                        │
        │  Embed Description (4096 characters).                               │
        │                                                                     │
        │                                                                     │
        │  [F](url.com)   MAX 256        FIELD 3                              │
        │  ‾‾‾            CHARACTERS                                          │
        │  Field 1 text.                 These fields                         │
        │                 These fields   can have as                          │
        │                 are inline     much text as                         │
        │                                you want.                            │
        │                                                                     │
        │  THESE FIELDS                                                       │
        │                                                                     │
        │  Are not.                                                           │
        │                                                                     │
        │  INLINE                                                             │
        │                                                                     │
        │  *Discord* **text** ~~formatting~~ `is`                             │
        │  [Supported](github.com/AlexanderHOtt)                              │
        │  \`\`\`md                                                              │
        │  # Code Blocks                                                      │
        │                                                                     │
        │  Code blocks are supported                                          │
        │  \`\`\`                                                                │
        │  > And quotes                                                       │
        │                                                                     │
        │                                                                     │
        │  ╭───────────────────────────────────────────────────────────────╮  │
        │  │                                                               │  │
        │  │                             Image                             │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  │                                                               │  │
        │  ╰───────────────────────────────────────────────────────────────╯  │
        │  ╭────╮                                                             │
        │  │    │  <- Footer Icon, Footer text · Today at 16:20               │
        │  ╰────╯                                                             │
        ╰─────────────────────────────────────────────────────────────────────╯
        """
        timestamp = datetime.datetime.now().astimezone()
        embed = hikari.Embed(title=title, description=desc, url=url, color=color or Colors.DEFAULT, timestamp=timestamp)

        embed.set_image(image)
        embed.set_author(name=header, url=header_url, icon=header_icon)
        embed.set_thumbnail(thumbnail if thumbnail is not ESCAPE_NAME else None)

        author = author or getattr(ctx_or_event, "author", None)
        EmbedFactory._set_footer(embed, footer, footer_icon, author, bot)

        if fields is not None:
            for field in fields:
                n, v, i = field
                embed.add_field(n, v, inline=i)

        return embed

    @staticmethod
    def _set_footer(
        embed: hikari.Embed,
        footer_text: str | None,
        footer_icon: ResourceishOrNoneT,
        author: hikari.User | None,
        bot: hikari.GatewayBot,
    ) -> hikari.Embed:
        if footer_text is ESCAPE_NAME:
            text = None
        elif footer_text is not None:
            text = footer_text
        elif author is not None:
            text = f"Invoked by {author.username}"
        else:
            text = None

        if footer_icon is ESCAPE_NAME or text is None:
            icon = None
        elif footer_icon is not None:
            icon = footer_icon
        elif author is not None:
            icon = author.avatar_url
        elif (me := bot.get_me()) is not None:
            icon = me.avatar_url or me.default_avatar_url
        else:
            icon = None

        return embed.set_footer(text=text, icon=icon)
