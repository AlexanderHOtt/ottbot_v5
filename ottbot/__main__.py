# -*- coding=utf-8 -*-
"""Main entry point for module cli."""
import os

import dotenv
import hikari
import lavasnek_rs
import tanjun

from ottbot import bot
from ottbot import config as config_

dotenv.load_dotenv()


class EventHandler:
    """Handles events from the Lavalink server."""

    async def track_start(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackStart) -> None:
        """Handles track start events."""
        print(f"Track started on guild: {event.guild_id}")

    async def track_finish(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackFinish) -> None:
        """Handles track finish events."""
        print(f"Track finished on guild: {event.guild_id}")

    async def track_exception(self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException) -> None:
        """Handles track exception events."""
        print(f"Track exception event happened on guild: {event.guild_id}")

        # If a track was unable to be played, skip it
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if skip and node:
            if not node.queue and not node.now_playing:
                await lavalink.stop(event.guild_id)


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    b, c = bot.build_bot()

    @c.with_listener(hikari.ShardReadyEvent)
    async def on_shard_ready(
        event: hikari.ShardReadyEvent,
        client_: tanjun.Client = tanjun.injected(type=tanjun.Client),
        config: config_.FullConfig = tanjun.inject(type=config_.FullConfig),
    ) -> None:
        """Event that triggers when the hikari gateway is ready."""
        if config.lavalink_password is None:
            return
        builder = (
            lavasnek_rs.LavalinkBuilder(event.my_user.id, config.tokens.bot)
            .set_host(config.lavalink_host)
            .set_password(config.lavalink_password)
            .set_start_gateway(False)
            # We set start gateway False because hikari can handle
            # voice events for us.
        )

        # Here we add lavasnek_rs.Lavalink as a type dependency to the client
        # We will use this later to have access to it in all our commands
        client_.set_type_dependency(lavasnek_rs.Lavalink, await builder.build(EventHandler))

    @c.with_listener(hikari.VoiceStateUpdateEvent)
    async def on_voice_state_update(
        event: hikari.VoiceStateUpdateEvent,
        lavalink: lavasnek_rs.Lavalink = tanjun.injected(type=lavasnek_rs.Lavalink),
    ) -> None:
        """Passes voice state updates to lavalink."""
        lavalink.raw_handle_event_voice_state_update(
            event.state.guild_id,
            event.state.user_id,
            event.state.session_id,
            event.state.channel_id,
        )

    @c.with_listener(hikari.VoiceServerUpdateEvent)
    async def on_voice_server_update(
        event: hikari.VoiceServerUpdateEvent,
        lavalink: lavasnek_rs.Lavalink = tanjun.injected(type=lavasnek_rs.Lavalink),
    ) -> None:
        """Passes voice server updates to lavalink."""
        if event.endpoint is not None:
            await lavalink.raw_handle_event_voice_server_update(
                event.guild_id,
                event.endpoint,
                event.token,
            )

    b.run()
