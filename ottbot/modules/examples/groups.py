# -*- coding=utf-8 -*-
"""Command Group Examples."""

"""
```
/example subcommand
/example subcommand2
/example subgroup command
/example subgroup command2

example
    subcommand
    subcommand2
    subgroup
        command
        command2
```
"""
import tanjun

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()

# example_group = tanjun.slash_command_group("example-group", "An example slash command group.")

# you can define groups like this, then you omit the @component.with_slash_command decorator
# although, it makes the commands less readable if you have multiple components in one file
example_group = component.with_slash_command(
    tanjun.slash_command_group("example-group", "An example slash command group.")
)


@example_group.with_command
@tanjun.as_slash_command("subcommand", "A subcommand in the example-group command.")
async def cmd_subcommand(ctx: tanjun.abc.SlashContext) -> None:
    """An example subcommand."""
    await ctx.respond("example-group\n  subcommand")


@example_group.with_command
@tanjun.as_slash_command("subcommand2", "A subcommand in the example-group command.")
async def cmd_subcommand2(ctx: tanjun.abc.SlashContext) -> None:
    """An example subcommand."""
    await ctx.respond("example-group\n  subcommand2")


example_sub_group = example_group.with_command(
    tanjun.slash_command_group("subgroup", "An example slash command sub group.")
)
# same with the top level groups, you can shorthand the subgroups
# example_sub_group = example_group.with_command(tanjun.slash_command_group("subgroup", "An example slash command sub group."))


@example_sub_group.with_command
@tanjun.as_slash_command("command", "A subgroup command.")
async def cmd_command(ctx: tanjun.abc.SlashContext) -> None:
    """Example subgroup command."""
    await ctx.respond("example-group\n  subgroup\n      command")


@example_sub_group.with_command
@tanjun.as_slash_command("command2", "A subgroup command.")
async def cmd_command2(ctx: tanjun.abc.SlashContext) -> None:
    """Example subgroup command."""
    await ctx.respond("example-group\n  subgroup\n      command2")
