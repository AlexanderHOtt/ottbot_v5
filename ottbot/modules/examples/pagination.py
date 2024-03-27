# -*- coding=utf-8 -*-
"""Pagination with yuyo."""
import hikari
import tanjun
import yuyo

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_slash_command
@tanjun.as_slash_command("example_pagination", "Example pagination with yuyo.")
async def cmd_example_pagination(
    ctx: tanjun.abc.SlashContext, component_client: yuyo.ComponentClient = tanjun.inject(type=yuyo.ComponentClient)
) -> None:
    """Example pagination with yuyo."""
    if ctx.guild_id is None:
        return

    # pages: IteratorT[EntryT] = iter(
    #     [
    #         ("a", hikari.Embed(description="fdsa")),
    #         ("asdf", hikari.UNDEFINED),
    #         ("asdfsdfa", hikari.Embed(description="embed")),
    #     ]
    # )

    pages = iter(
        [
            ("page 1\nok", hikari.UNDEFINED),
            (hikari.UNDEFINED, hikari.Embed(description="page 2")),
            ("page3\nok", hikari.Embed(description="page3")),
        ]
    )
    paginator = yuyo.ComponentPaginator(pages, authors=(ctx.author.id,))

    first_page = await paginator.get_next_entry()
    assert first_page, "it should never be None"
    message = await ctx.respond(content=first_page[0], embed=first_page[1], component=paginator, ensure_result=True)
    component_client.set_executor(message, paginator)
