import configparser
import logging
import time

import osu_ds
from discord import Embed, Colour, errors

from core.stats import MESSAGE
from core.utils import is_valid_command, invert_num, invert_str, split_every
from core.configuration import PARSER_CONFIG

#####
# osu! plugin
#####

logger = logging.getLogger(__name__)

commands = {
    "_osu": {"desc": "Displays stats for that osu! user.", "use": "[command] [username/id]"},
}

valid_commands = commands.keys()


# About inverting: this inverts the number before and after the splitting
# Makes the number formatted
# 1000 -> 1,000
def prepare(this):
    if this is None:
        return None

    return invert_str(",".join(split_every(str(invert_num(this)), 3)))


class Osu:
    def __init__(self, **kwargs):
        self.nano = kwargs.get("nano")
        self.client = kwargs.get("client")
        self.stats = kwargs.get("stats")
        self.trans = kwargs.get("trans")

        try:
            key = PARSER_CONFIG.get("osu", "api-key")
            self.osu = osu_ds.OsuApi(api_key=key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.critical("Missing api key for osu!, disabling plugin...")
            raise RuntimeError

    async def on_message(self, message, **kwargs):
        trans = self.trans

        prefix = kwargs.get("prefix")
        lang = kwargs.get("lang")

        # Check if this is a valid command
        if not is_valid_command(message.content, commands, prefix):
            return
        else:
            self.stats.add(MESSAGE)

        def startswith(*matches):
            for match in matches:
                if message.content.startswith(match):
                    return True

            return False

        if startswith(prefix + "osu"):
            username = message.content[len(prefix + "osu "):]

            if not username:
                await message.channel.send(trans.get("MSG_OSU_NO_NAME", lang))
                return

            t_start = time.time()

            await message.channel.trigger_typing()
            user = await self.osu.get_user(username)

            if not user:
                await message.channel.send(trans.get("ERROR_NO_USER2", lang))
                return

            MISSING = trans.get("MSG_OSU_MISSING_PARAM", lang)

            global_rank = prepare(user.world_rank)
            if not global_rank:
                global_rank = MISSING
            country_rank = prepare(user.country_rank)
            if not country_rank:
                country_rank = MISSING

            total_score = prepare(user.total_score)
            if not total_score:
                await message.channel.send(trans.get("MSG_OSU_NOT_ENOUGH_PLAYS", lang))
                return

            ranked_score = prepare(user.ranked_score)

            try:
                acc = "{} %".format(round(float(user.accuracy), 2))
            except TypeError:
                acc = trans.get("INFO_ERROR", lang)

            pp_amount = int(float(user.pp))
            osu_level = int(float(user.level))
            avatar_url = user.avatar_url

            # Color is determined by the level range
            if osu_level < 10:
                color = Colour.darker_grey()
            elif osu_level < 25:
                color = Colour.light_grey()
            elif osu_level < 40:
                color = Colour.dark_teal()
            elif osu_level < 50:
                color = Colour.teal()
            elif osu_level < 75:
                color = Colour.dark_purple()
            elif osu_level < 100:
                color = Colour.purple()
            # Only masters get the gold ;)
            else:
                color = Colour.gold()

            desc = trans.get("MSG_OSU_DESC", lang).format(global_rank, user.country, country_rank, pp_amount, user.playcount)
            name = trans.get("MSG_OSU_TITLE", lang).format(user.name, osu_level)

            embed = Embed(url=user.profile_url, description=desc, colour=color)
            embed.set_author(name=name)
            embed.set_thumbnail(url=avatar_url)

            embed.add_field(name=trans.get("MSG_OSU_TOTAL_SC", lang), value=total_score)
            embed.add_field(name=trans.get("MSG_OSU_RANKED_SC", lang), value=ranked_score)
            embed.add_field(name=trans.get("MSG_OSU_AVG_ACC", lang), value=acc)

            delta = int((time.time() - t_start) * 1000)
            embed.set_footer(text=trans.get("MSG_OSU_TIME", lang).format(delta))

            try:
                await message.channel.send(embed=embed)
            except errors.HTTPException:
                await message.channel.send(trans.get("MSG_OSU_ERROR", lang))


class NanoPlugin:
    name = "osu!"
    version = "9"

    handler = Osu
    events = {
        "on_message": 10
        # type : importance
    }
