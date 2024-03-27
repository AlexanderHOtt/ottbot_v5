# -*- coding=utf-8 -*-
"""Example slash commands with autocomplete."""

import tanjun

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


async def _word_autocomplete(ctx: tanjun.abc.AutocompleteContext, partial_word: str) -> None:
    """The autocomplete function for cool words.

    Parameters
    ----------
    ctx : tanjun.abc.AutocompleteContext
        The context of the autocomplete, autofilled by tanjun.
    partial_word : str
        The partial word that the user has typed in, it will be filled incrementally
        like 'l' -> 'lm' -> 'lma' -> 'lmao' as the user types it.
    """
    words = ["ottbot", "is", "a", "great", "discord", "bot", "lmao"]
    # you will most likely use `in` or `.startswith()` to narrow down the choices
    await ctx.set_choices({x: x for x in words if x.startswith(partial_word)})


@component.with_slash_command
@tanjun.with_str_slash_option("word", "A cool word", autocomplete=_word_autocomplete)
@tanjun.as_slash_command("example_autocomplete", "An example slash command with autocomplete.")
async def cmd_example_autocomplete(ctx: tanjun.abc.SlashContext, word: str) -> None:
    """Example autocomplete slash command."""
    await ctx.respond(f"{word} is a pretty cool word!")
