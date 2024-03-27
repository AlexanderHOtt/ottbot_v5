# -*- coding=utf-8 -*-
"""Member update event listener."""

import logging

import hikari
import sake
import tanjun

from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.embeds import EmbedFactory, FieldsT
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.MemberUpdateEvent)
async def lsnr_ban_create(
    event: hikari.MemberUpdateEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Member update event listener."""
    if event.old_member is None:
        return
    if (
        config := await db.row("SELECT * FROM guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig)
    ) is None or config.log_channel_id is None:
        return

    old = event.old_member
    new = event.member
    fields: FieldsT = []
    image = None

    if old.avatar_url != new.avatar_url:
        if old.avatar_url is not None:
            fields.append(("New Profile Picture", "Old profile picture attached below", True))
            image = old.avatar_url
        else:
            fields.append(("New Profile Picture", "This user has not had a profile picture before.", True))

    if old.display_avatar_url != new.display_avatar_url:
        if old.display_avatar_url is not None:
            fields.append(("New Server Profile Picture", "Old profile picture attached below", True))
            image = old.display_avatar_url
        else:
            fields.append(("New Server Profile Picture", "This user has not had a profile picture before.", True))

    if (r1 := old.get_roles()) != (
        r2 := await new.fetch_roles()
    ):  # Don't fetch old roles because those would be the new ones
        difference = set(r1).symmetric_difference(set(r2))
        fields.append(("Role Update", " ".join(r.mention for r in difference), True))

    if old.nickname != new.nickname:
        fields.append(("Nickname Update", f"Old nick: {old.nickname}\nNew nick: {new.nickname}", True))

    if old.username != new.username:
        fields.append(("Username Update", f"Old name: {old.username}\nNew name: {new.username}", True))

    if old.discriminator != new.discriminator:
        fields.append(
            (
                "Discriminator Update",
                f"Old discriminator: {old.discriminator}\nNew discriminator: {new.discriminator}",
                True,
            )
        )

    embed = EmbedFactory.build(event, bot, title="User Update", fields=fields, image=image)
    await bot.rest.create_message(config.log_channel_id, embed=embed)
