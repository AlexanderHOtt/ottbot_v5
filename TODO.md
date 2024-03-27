# TODO

## General

- [ ] Normalize Embed footers for events
- [-] custom colors for event types
- [ ] fix yuyo client response in auto_roles
  - [ ] explore how select menus work
- [ ] fix module structure and add command groups where necessary
- [ ] use `logging.exception` for exceptions

## Features

- [ ] help command
- [ ] refactor music commands
- [ ] add more music commands
- [ ] guild config
- [-] starboard
  - [x] basic logic
  - [ ] advanced logic
    - [ ] channel whitelist and blacklist
    - [ ] minimum number of stars
  - [ ] ui
- [ ] currency
  - [ ] daily roll
  - [ ] randomly appearing bosses
- [ ] tags
  - [ ] basic logic
- [ ] track more info with command.metadata
- [ ] voting rewards

## Reogranise modules and commands

command = slash command, prefix command, user app, message app
if a function is defined in an init file, it cannot be reloaded by the command client,
the whole python instance needs to be restarted unless some `inspect` black magic is used
to redefine function bodies at runtime / import previously unimported modules

a bot can have at most 100 slash commands declared, so the max number of files in the modules folder would be around 100 (not including **init** files)

1. each command has its own file
   i. cmd groups are imported from an **init**.py file
2. each command group has its own file
   i. cmd groups are stored locally in the file
3. commands that share functionality have the same file
   i. `_ban_member` is defined locally and the /ban, $ban, ban message app, and ban user app are all defined in the same file.
4. commands that share a theme share the same file
   i. /ban ..., /kick ..., /warn ..., /timeout are all in the same file.

- 1 pros
  - can [re|un]load commands, cmd groups, and full modules individually, this method has the most control over what is loaded
  - follows the 'small file' principle
- 1 cons
  - Module folder would get really bloated
  - some functions and components need to be imported from the **init**.py file, meaning they aren't re-registered with a /update
  - ~~local imports are painful~~.
  - repeated code
- 2 pros
  - [re|un]load cmd groups individually
  - still follows the 'small file' principle
  - no need to import a group from an **init** file
  - some functions can be defined locally
- 2 cons
  - lose ability to reload commands specifically
  - still need to import some functions from an **init** file
- 3 pros
  - no functions (defined in the modules folder) need to be imported locally
  - commands that are similar are defined in the same file
- 3 cons
  - lose more control over what is loaded
- 4 pros
  - least amount of files in modules folder
- 4 cons
  - very little control over what is loaded
  - file size is very large (500+ lines)

### Solution

mix between 2 and 3

### Rules

1. Command group commands share a file
   1. should sub command groups share the same file
1. Commands that share functionality share a file
