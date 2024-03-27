# -*- coding=utf-8 -*-
"""Play or queue a song."""

import hikari
import lavasnek_rs
import tanjun

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


async def _join_voice(ctx: tanjun.abc.Context, lavalink: lavasnek_rs.Lavalink) -> hikari.Snowflake | None:
    if ctx.guild_id is None:
        return

    if ctx.client.cache and ctx.client.shards:
        if (voice_state := ctx.client.cache.get_voice_state(ctx.guild_id, ctx.author)) is None:
            await ctx.respond("Please join a voice channel.")
            return

        await ctx.client.shards.update_voice_state(ctx.guild_id, voice_state.channel_id, self_deaf=True)

        conn = await lavalink.wait_for_full_connection_info_insert(ctx.guild_id)

        await lavalink.create_session(conn)
        return voice_state.channel_id

    await ctx.respond("Unable to join channel. The cache is disabled or shards are down.")


async def _play_track(ctx: tanjun.abc.Context, song: str, lavalink: lavasnek_rs.Lavalink) -> None:
    if ctx.guild_id is None:
        return

    conn = lavalink.get_guild_gateway_connection_info(ctx.guild_id)

    if not conn:
        if not _join_voice(ctx, lavalink):
            return

    if not (tracks := (await lavalink.auto_search_tracks(song)).tracks):
        await ctx.respond(f"Could not find any songs for {song}")
        return

    try:
        await lavalink.play(ctx.guild_id, tracks[0]).requester(ctx.author.id).queue()

    except lavasnek_rs.NoSessionPresent:
        await ctx.respond("Unable to join voice, this may be an internal error.")
        return

    await ctx.respond(f"Added to queue: `{tracks[0].info.title}`")


@component.with_slash_command
@tanjun.as_slash_command("join", "Connect the bot to a voice channel.")
async def cmd_join(
    ctx: tanjun.abc.Context,
    lavalink: lavasnek_rs.Lavalink = tanjun.injected(type=lavasnek_rs.Lavalink),
) -> None:
    """Join a voice channel."""
    if channel_id := await _join_voice(ctx, lavalink):
        await ctx.respond(f"Joined <#{channel_id}>")


@component.with_slash_command
@tanjun.with_str_slash_option("name", "The name of the song")
@tanjun.as_slash_command("play", "Play or queue a song.")
async def cmd_play(
    ctx: tanjun.abc.Context,
    name: str,
    lavalink: lavasnek_rs.Lavalink = tanjun.injected(type=lavasnek_rs.Lavalink),
):
    """Play a song."""
    await _play_track(ctx, name, lavalink)
