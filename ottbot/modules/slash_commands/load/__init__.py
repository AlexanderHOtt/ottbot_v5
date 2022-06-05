# -*- coding=utf-8 -*-
"""Commands for loading and unloading other commands."""

import tanjun

from ottbot.utils.funcs import get_list_of_files, path_to_module


async def autocomplete_path(ctx: tanjun.abc.AutocompleteContext, module: str) -> None:
    """Autocomplete for modules."""
    all_modules = get_list_of_files()
    await ctx.set_choices(
        {path_to_module(m): m.as_posix() for m in all_modules if module in m.as_posix().replace("/", ".")}
    )
