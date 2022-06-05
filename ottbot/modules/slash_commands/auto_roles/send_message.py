# -*- coding=utf-8 -*-
"""Send the autorole message."""
import functools
import logging

import hikari
import tanjun
import yuyo
from ottbot.db.records import AutoRole

from ottbot.utils.funcs import build_loaders
from ottbot.db import AsyncPGDatabase

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


async def _add_role(
    ctx: yuyo.ComponentContext,
) -> None:
    logger.info("INSIDE Callback")
    if ctx.interaction.member is None:
        return
    role_id = int(ctx.interaction.custom_id.split(";")[-1])
    try:
        await ctx.interaction.member.add_role(role_id, reason="auto role")
        await ctx.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, f"Gave you <@&{role_id}>", flags=hikari.MessageFlag.EPHEMERAL
        )
    except hikari.ForbiddenError:
        await ctx.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, "Not enough permissions.", flags=hikari.MessageFlag.EPHEMERAL
        )


@component.with_slash_command
@tanjun.with_channel_slash_option(
    "channel",
    "The channel to send the message in, defaults to the current channel.",
    types=[hikari.TextableGuildChannel],
    default=None,
)
@tanjun.as_slash_command("send_autorole_message", "Register an autorole.", default_to_ephemeral=True)
async def cmd_send_autorole(
    ctx: tanjun.abc.SlashContext,
    channel: hikari.TextableGuildChannel | None,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
    component_client: yuyo.ComponentClient = tanjun.inject(type=yuyo.ComponentClient),
) -> None:
    """Send the autorole message."""
    if ctx.guild_id is None:
        return
    channel_id = channel.id if channel else ctx.channel_id

    if not (
        auto_roles := await db.rows("SELECT * FROM auto_roles WHERE guild_id = $1", ctx.guild_id, record_cls=AutoRole)
    ):
        await ctx.respond("No autoroles registered.")
        return

    # ids: list[tuple[str, str]] = []
    # for role in auto_roles:
    #     custom_id = f"AUTOROLE;{ctx.guild_id};{role.role_id}"
    #     cb = component_client.get_constant_id(custom_id)
    #     logger.info(cb)
    #     if cb is None:
    #         component_client.set_constant_id(custom_id, _add_role)
    #     ids.append((custom_id, role.role_name))
    #
    # row = ctx.rest.build_action_row()
    # for id, name in ids[:5]:
    #     row.add_button(hikari.ButtonStyle.SECONDARY, id).set_label(name).set_emoji("➕").add_to_container()
    # msg = await ctx.rest.create_message(channel_id, "Select a role", components=[row])
    # await ctx.create_initial_response(f"Sent message in <#{channel_id}>, [jump]({msg.make_link(ctx.guild_id)})")

    row = ctx.rest.build_action_row()
    menu = row.add_select_menu(f"AUTOROLE;{ctx.guild_id}")
    for autorole in auto_roles:
        id = f"AUTOROLE;{ctx.guild_id};{autorole.role_id}"
        menu.add_option(autorole.role_name, id).set_description("asdf").set_emoji("➕").add_to_menu()
        component_client.set_constant_id(id, _add_role)
    menu.set_placeholder("-- Select a role --").add_to_container()

    await ctx.rest.create_message(channel_id, "Select a role", component=row)
