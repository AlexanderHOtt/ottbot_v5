# -*- coding=utf-8 -*-
"""Main entry point for module cli."""
import os

import dotenv

from ottbot import bot

dotenv.load_dotenv()


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    b, c = bot.build_bot()

    b.run()
