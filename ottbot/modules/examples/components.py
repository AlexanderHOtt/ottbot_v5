# -*- coding=utf-8 -*-
"""Discord components."""
import hikari
import tanjun
import yuyo

from ottbot.constants import ZWJ
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_slash_command
@tanjun.as_slash_command("example_button", "Button example.")
async def cmd_example_button(ctx: tanjun.abc.SlashContext) -> None:
    """Discord button example."""
    if ctx.guild_id is None:
        return

    row = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.PRIMARY, "example_button_id")
        .set_label("Click Me")
        .add_to_container()
    )
    row2 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "example_button_id;OK")
        .set_emoji("✅")
        .add_to_container()
        .add_button(hikari.ButtonStyle.DANGER, "example_button_id;CANCEL")
        .set_emoji("❌")
        .add_to_container()
    )
    row3 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.LINK, "https://github.com/AlexanderHOtt/ottbot_v4")
        .set_label("Github Repo")
        .add_to_container()
    )
    # you can have up to 5 buttons per row, and 5 rows per message
    await ctx.respond("Buttons", component=row)
    await ctx.create_followup(ZWJ, components=[row2, row3])


@component.with_slash_command
@tanjun.as_slash_command("example_select_menu", "Select menu example.")
async def cmd_example_select_menu(ctx: tanjun.abc.Context) -> None:
    """Select menu example."""
    if ctx.guild_id is None:
        return

    row = (
        ctx.rest.build_action_row()
        .add_select_menu("example_menu_id")
        # option 1
        .add_option("Red", "Red")
        .set_emoji("🔴")
        .add_to_menu()
        # option 2
        .add_option("Green", "Green")
        .set_description("green green what's your problem")
        .set_emoji("🟢")
        .add_to_menu()
        # option 3
        .add_option("Blue", "Blue")
        .set_emoji("🔵")
        .add_to_menu()
        .add_to_container()
    )

    await ctx.respond("The choice is yours", component=row)


# To add functionality to the buttons and menus, you need to register a callback on the custom_id
# I use yuyo, but there is miru, and you could always do it yourself


@component.with_slash_command
@tanjun.as_slash_command("example_button_cb", "Example button callback.")
async def cmd_example_cb(
    ctx: tanjun.abc.SlashContext, component_client: yuyo.ComponentClient = tanjun.inject(type=yuyo.ComponentClient)
) -> None:
    """Example button callback with yuyo."""
    if ctx.guild_id is None:
        return

    custom_id = "example_button_cb;yuyo_callback"

    async def yuyo_callback(ctx: yuyo.ComponentContext) -> None:
        await ctx.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f"{ctx.interaction.member.mention if ctx.interaction.member else 'You '} clicked the button!",
        )

    if component_client.get_constant_id(custom_id) is None:
        component_client.set_constant_id(custom_id, yuyo_callback)

    row = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, custom_id)
        .set_label("Click me!")
        .add_to_container()
    )

    await ctx.respond("Yuyo!", component=row)


@component.with_slash_command
@tanjun.as_slash_command("example_select_menu_cb", "Example select menu callback.")
async def cmd_example_select_menu_cb(
    ctx: tanjun.abc.SlashContext, component_client: yuyo.ComponentClient = tanjun.inject(type=yuyo.ComponentClient)
) -> None:
    """Example select menu with yuyo callbacks."""
    if ctx.guild_id is None:
        return

    custom_id = "example_select_menu_cb;yuyo_callback"

    async def yuyo_menu_cb(ctx: yuyo.ComponentContext) -> None:
        ...

    if component_client.get_constant_id(custom_id) is None:
        component_client.set_constant_id(custom_id, yuyo_menu_cb)

    options: list[tuple[str, str, str | None, hikari.Emoji | hikari.Snowflakeish]] = []

    menu = (row := ctx.rest.build_action_row()).add_select_menu(custom_id)

    for key, value, desc, emoji in options:
        option = menu.add_option(key, value)
        if desc:
            option.set_description(desc)
        if emoji:
            option.set_emoji(emoji)
        option.add_to_menu()
    menu.add_to_container()

    await ctx.respond("Select some options", component=row)
