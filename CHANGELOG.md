3.8.1
- Bug fixes (!setup)
- New step for !setup - invite filtering

3.8
- Transitioned to two redis dbs: one for data and one as a cache
- Simplified !imdb usage
- Renamed !vote start/end/status to !poll start/end/status
- Usage overhaul for !poll start
- Rate-limiting of commands prevent abuse
- More confirmations for stuff
- Optimizations

3.7.6
- !joke now has no parameters, but has a much bigger pool of jokes
- !setup is now more beautiful than ever
- Bugfixes


3.7.5
- Added !achievement generator
- Raised cmd response length cap to 1000
- Bugfixes

3.7.4
- Updated !randomgif with optional keywords
- Added arguments to !cmds
- Bugfixes

3.7.2
Bug fixes from the previous version

3.7 and 3.7.1
Read http://nanobot.pw/changelog.html

3.6.1
- Bugfixes from previous release
- Additional messages for different cases
- Fixed exploits in !selfrole

3.6
- Dropped support for the old storage system
- Added multi language support!
- Bugfixes
- More possibilities covered with convert_to_seconds

3.5.1
- !notifydev has been renamed to !report
- Latest number of xkcd comics is now checked every 6 hours
- Bugfixes and typos

3.5
- Brought back the movie/tv search, provided by The Movie Database
- Even more bugfixes
- More foolproof

3.4.9
- More bugfixes (they never end)
- New setting: default channel (for join/ban/leave messages)
- Nano now logs !say to the logchannel

3.4.8
- Bugfixes
- More sophisticated word filter
- New logging stuff

3.4.7
- New feature: selfrole! (commands: !selfrole [role name], nano.settings selfrole [role name])
- Bugfixes

3.4.6
- Bugfixes
- Some logging changes (now with bug reporting)
- More caching for all the speeeed
- Refactorings

3.4.5
- Bugfixes
- New plugin! jokes - features random jokes, cat pictures and xkcd
- Fixed help message (not fixed before)

3.4.4
- !imdb/!omdb rewritten
- Changed syntax for !softban
- Bugfixes

3.4.3
- More bugfixes ¯\_(ツ)_/¯

3.4.2
- Bugfixes

3.4.1
- New command: !server - displays server info
- Bugfixes

3.4
- New: Redis support!
- Ability to convert old data to the new system
- Additional settings in settings.ini to allow using legacy server data system
- Help message fix
- Added some common bots to ignore (to prevent circular commands)
- Bugfixes and adaptions to redis
- Various speed improvements

3.3.3
- Text changes
- Bugfixes

3.3.2
- Bugfixes

3.3.1
- Fixed moderator permissions

3.3
- New !help system
- Added back nano.blacklist
- Added "Nano Mod" permission

3.2.3
- Bugfixes

3.2.2
- Added back !unban
- There is now a command (35) and vote option limit (10)
- Added !vote status and !cmd status
- Bugfixes

3.2.1
- !suggest and !report cooldown implementation because people were spamming it
- Bugfixes
- Utils now includes StandardEmoji for quick access to emojis
- Added meme generator

3.2
- Can now RELOAD plugins! (nano.dev.plugin.reload <name> as owner)
- More bugs fixed (they never stop coming)
- ping command now includes difference between message timestamp and sending time in ms
- fixed and stylised help command
- Fixed !tf issues
- Added !osu

3.1.post4
- A bugfix

3.1.4
- Updated some commands to the new Embed format
- More bugfixes
- Log channel can now be changed with nano.settings logchannel [name]

3.1.3
- Bugfixes

3.1.2
- Bugfixes
- :username can now also be used as a join/leave/...-message variable
- Setting any of the join/leave/...-messages to None/Off/False will disable that command

3.1.1
- Fixed backup plugin
- Fixed moderation (now ignores all commands)
- Bugfixes

3.1.0
- Added !debug (ram, cpu, reminder, voting, versions, uptime info)
- Fixed status roller and upped it up to 6 hours for one status
- Added some stats integrations back
- A success of a vote is now acknowledged with :ok_hand: for 1.5 sec
- Moderation logs are now sent to the log channel every minute

3.0.4
- Improved spam detection (now excludes links and messages shorter than 10 characters)

3.0.3
- Added !setup / nano.setup (previously as !getstarted)
- Added Forbidden 403 error logging to log.txt
- Updated !help [command]
- Some bugfixes

3.0.2
- Reminders now persist between restarts!
- Raised the reminder limit to 2 (temporarily?)
- Added an event - ON_SHUTDOWN

3.0.1
- Softbanning and reminders were not reliable, this update fixes that
- Some bugs?

v3.0
- Completely rewritten (a new plugin system)
- Fixed some bugs
- Fixed muting

2.2.4
- Added Cards For Humanity lobby generation
- Added osu! user search
- Small bugfixes

2.2.3
- Small changes and bugfixes
- Some Refactorings and PEP8 fixes
- Added if __name__ = "main" block

2.2.2
- Small message changes
- Added softbanning (!softban [time] @mention)
- Fixed imdb search and grammar mistakes

2.2.1
- Now removing servers from servers.yml in on_server_remove
- Fixed a bug involving Nano mentions
- Fixed a bug with user muting
- Stats module optimizations (amount of read operations decreased)
- Added !remind

2.2
- Added logging to most of the modules
- Added IMDB.com search
- Fixed a bug where bot would not check some servers on startup

2.1.9
- Added !nuke for mass deleting messages
- Fixed a bug where stats.yml.bak2 would be a server file
- Fixed a bug where missing vars would not get added to servers.yml
- Fixed a bug where some settings would not get changed because the use of two words instead of one
- Performance optimizations
- Added invite detection and removal

2.1.8
- ServerHandler is now more efficient (less reads/writes) and a singleton
- Fixed some messages
- Fixed !getstarted settings wrong things and added another step
- Fixed unnecessary servers.yml writes at bot startup

2.1.7
- Added POSTing server count to bots.discord.pw
- Fixed !steam help message

2.1.6
- Changed admin role from "Admin" to "Nano Admin"
- Log channel now gets created if one does not exist.
- Small text changes
- Added restart functionality
- !help command now shows owner commands

2.1.5
- Small changes
- Backup module added
- Now runs on one loop instead of two
- Added random status change every 30 minutes

2.1.4
- Bugfixes
- AyyBot has been renamed to Nano! (ayybot.* is now nano.* and !ayybot is !nano)

2.1.3a/b
- Optmizations and bugfixes
- !tf added
- Fixed ayybot.wake bug
- Reworked help system
- Added vote saving between restarts
- KeyboardInterrupt handler
- More server settings added (custom welcome, ban and kick message)

2.1.2
- !johncena command removed
- Redundant console prints removed
- !help command: fixed too many newlines
- Added commands: _mc/_minecraft and _steam/_steam friends/_steam games
- Set up logging module for easy debugging

2.1.1
- Replaces time.sleep calls with asyncio.sleep
- Fixed bugs
- Shortened code for 'playing' status change
- Added logging to log.txt
- Added a special debugging mode

2.1
- More @ayybot mention responses
- Completely new spam detection (2 character markov chain based detection)
- Muting feature

v2.0!
- Code rewritten from ground up!
- Some useless features have been removed, many new added
- Cleaner, faster code

1.6.4
- Added +eval/+calc and +exec (only for admins, has detection for potentially dangerous code, which only the owner can run)
- Updated +user with account creation date
- Added missing permission exception for +role command
- Fixed many bugs that happened in private messages
- Added ayybot.changeavatar, +download, +dlmanage
- Changed style of some replies
- Added +timetosec just for fun

1.6.3
- Fixed some bugs

1.6.2
- Per-server settings (a bunch of commands were added):
  Almost every aspect of the bot can now be customized on server basis:
  -> Sleeping, commands, channel blacklists, admins, filtering spam and swearing, logchannel and join message.
- Fixed some bugs
- +cmd add now uses ++ and "" as split points
- Optimizations
- Now the user must supply a token (requires a bot account)

1.6.1
- Fix : The bot would keep filtering messages even if in sleep mode
- Fix : The bot would keep filtering spam even if disabled in settings.ini
- Fixed some commands not working with any other prefix than !
- Fixed !cmd add always adding ! as prefix, as of now you must specify your own prefix in <trigger>
- Fixed status in settings.ini not working as expected
- Fixed !help all public not working
- Added the ability to disable game time monitoring in settings.ini
- Game time now uses id's instead of usernames!
- Custom commands are now divided by (), allowing you to respond with emojis
- Optimized stuff and organised help commands
By the way, wiki has been added :)

1.6
- Improved spam detection, removed "Spam is not allowed" message.
- Fixed some variables in settings.ini not working
- Changed code layout (kind of)
- Removed !game, was useless
- Added game time monitoring. :
    !games - tells you amount of every game you played
- Added bot startup time to log.txt
- @Nano say <something> now responds with tts
- "!help all" has changed, now sends to private message, "!help all public" works as before
- Added customizable !help delay in settings.ini

1.5
- Fixed no join message, can now also be disabled in settings.ini
- Fixed !cmd list not working
- You can now shut down the bot, even if in sleep mode
- Optimized !role command
- Added ayybot.config.reload, which reloads settings.ini
- Added ayybot.whitelist.reload, which reloads the whitelist
- Added comments in settings.ini for better understanding

1.4
- Fixes
- Changed !role command:
    !role add <role name> @mention - adds roles
    !role remove <role name> @mention - removes roles
    !role replacewith <role name> @mention - replaces all roles with <role name>
  Now supports all roles present on the server.

1.3
- Fixes and "optimizations"
- Added !playing <game> - to change "playing" status
- Removed state_sleep and lasttime from settings.ini - now using classes
- Added !vote start/end or number - votes (currently supports up to 5 choices)
- Added custom prefix (in settings.ini)

1.2
- Added status (configurable in settings.ini)
- Fixed whitelist
- Changed logging "separator" to two newlines
- Fixed !credits
- Added !define which is the same as !wiki

1.1
- UPDATED TO ASYNC API (0.10 version)
- Bugfixes
- Added whitelist (commands to be added)
- Fixed logging to 'logs' showing unchanged messages with links
- Added customization for the name of log channel
- Fixed !hello

0.17
- Fixed missing cmds in !help
- Added some missing logdis(message)
- Added !hi @<user> for a bot so say to someone
- Added rate limit for !help, might add global rate limit in the future
- Added customizable number of !wiki sentences to settings.ini
- Added "multiple definitions found" for !wiki

0.16
- Moved some code
- Some !role "fixes" and changes
- Fixed spaces in !game
- Moved credentials to settings.ini
- Added message deletion and editing monitor that logs into "logs" channel
- Fixed double names showing up in !member
- Added "no urban definition found" for !urban and modified some code
- Added !cmd for adding commands on the fly
- Moved some files
- "BIG UPDATE" Added ability to add/list/remove commands with:
    !cmd add <trigger> <response>
    !cmd list
    !cmd remove !<name>

0.15
- Added "no definition found" exception for !wiki and changed the format
- Added !help all
- Changed !manage sleep/wake to ayybot.sleep/wake
- Grammar
- Added state_sleep to settings.ini
- Moved filtering words to config.py
- Changed !listmembers to !members
- Excluded the bot from spam check

0.14
- Optimized some code
- Added !wiki <query> (requires wikipedia lib)
- Added !urban <query>

0.13
- Added permission check for !role
- Grammar fixes
- Added !manage sleep/normal
- Changed !shutmedown to ayybot.kill and !restart to ayybot.reboot
- Changed !moreayy to !ayylmao
- Grammar fixes, ...

0.12
- Added !quote - returns random quotes
- Added !role mod/removemod/members @mentions
- Added permission check for !restart and !shutmedown
- Fixed !restart error
- Moved creds to config.py
- Fixed logging for some commands

0.11
- Fixed spaces in !gif
- Replaced !test with !ping
- removed !who from config.py, now it's !user @mention
- Fixed word filter (now using wordfilter module)
