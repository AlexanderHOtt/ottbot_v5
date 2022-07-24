# -*- coding=utf-8 -*-
"""Main entry point for module cli."""
import os

import dotenv

from ottbot import bot
from ottbot.version import VERSION

dotenv.load_dotenv()


# logging is handled by hikari, but hikari isn't initialized until `bot.run()` is called
print(  # noqa: T001
    rf"""
  _______             ______                      _______     OttBot v{VERSION}
 (_______)  _     _  (____  \        _           (_______)
  _     _ _| |_ _| |_ ____)  ) ___ _| |_    _   _ ______      GitHub:  https://github.com/AlexanderHOtt/ottbot_v5
 | |   | (_   _|_   _)  __  ( / _ (_   _)  | | | (_____ \     Discord: ...
 | |___| | | |_  | |_| |__)  ) |_| || |_    \ V / _____) )
  \_____/   \__)  \__)______/ \___/  \__)    \_/ (______/
"""
)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    b, c = bot.build_bot()

    b.run()
