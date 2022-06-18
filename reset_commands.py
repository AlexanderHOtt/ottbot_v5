# -*- coding=utf-8 -*-
"""Reset the slash commands for the bot."""
import asyncio

import hikari

rest = hikari.RESTApp()
BOT_ID = 866821214316003339


async def main():
    """Run the bot and reset the slash commands."""
    async with rest.acquire("token", hikari.TokenType.BOT) as client:
        await client.set_application_commands(BOT_ID, [])


asyncio.run(main())
