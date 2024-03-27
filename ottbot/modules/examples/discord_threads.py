# -*- coding=utf-8 -*-
"""Example slash commands."""


import hikari

import tanjun
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_slash_command
@tanjun.as_slash_command("example_thread", "Create a thread", default_to_ephemeral=True)
async def cmd_example_thread(ctx: tanjun.abc.SlashContext):
    """Example thread command."""
    channel = await ctx.rest.create_thread(
        ctx.channel_id, hikari.ChannelType.GUILD_PUBLIC_THREAD, "test", auto_archive_duration=60
    )
    await ctx.respond("Thread created!")
    await channel.send(f"This is a thread, {ctx.author.mention}!", user_mentions=True)
    # await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE)
    # await ctx.rest.create_thread(ctx.channel_id, name="test thread", auto_archive_duration=60)

    # event = await bot.wait_for(
    #     hikari.InteractionCreateEvent,
    #     timeout=69,
    #     predicate=lambda e: isinstance(e.interaction, hikari.ModalInteraction),
    # )

    # await event.interaction.app.
