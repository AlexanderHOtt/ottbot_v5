# -*- coding=utf-8 -*-
"""Example slash commands."""


# import hikari
# from hikari.impl.bot import GatewayBot

# import tanjun
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


# @component.with_slash_command
# @tanjun.as_slash_command("example_modal", "An example modal")
# async def cmd_example_modal(ctx: tanjun.abc.SlashContext, bot: GatewayBot = tanjun.inject(type=GatewayBot)j):
#     """Example modal command."""
#     row = ctx.rest.build_modal_action_row().add_text_input("example_modal_button", "Click Me").add_to_container()
#     await ctx.interaction.create_modal_response("Example Modal", "This is an example modal", row)

#     event = await bot.wait_for(
#         hikari.InteractionCreateEvent,
#         timeout=69,
#         predicate=lambda e: isinstance(e.interaction, hikari.ModalInteraction),
#     )

#     await event.interaction.app.
