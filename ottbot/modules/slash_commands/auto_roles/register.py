# -*- coding=utf-8 -*-
"""Register an autorole."""
import logging

import hikari
import tanjun
from ottbot.db.records import AutoRole

from ottbot.utils.funcs import build_loaders
from ottbot.db import AsyncPGDatabase

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_slash_command
@tanjun.with_role_slash_option("role", "The role to register.")
@tanjun.as_slash_command("register_autorole", "Register an autorole.", default_to_ephemeral=True)
async def cmd_register_autorole(
    ctx: tanjun.abc.SlashContext, role: hikari.Role, db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase)
) -> None:
    """Register an autorole."""
    if auto_roles := await db.rows("SELECT * FROM auto_roles WHERE guild_id = $1", ctx.guild_id, record_cls=AutoRole):
        if int(role.id) in [r.role_id for r in auto_roles]:
            await ctx.respond("Role is already registered.")
            return

    await db.execute(
        "INSERT INTO auto_roles (guild_id, role_id, role_name) VALUES ($1, $2, $3)", ctx.guild_id, role.id, role.name
    )
    await ctx.respond(f"Registered autorole for {role.mention}", role_mentions=False)
