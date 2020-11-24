# coding=utf-8
import redis
import logging
import time
import os

from discord import Member, Guild
from .utils import Singleton, decode, bin2bool
from .exceptions import SecurityError
from .confparser import get_settings_parser, get_config_parser

__author__ = "DefaltSimon"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# plugins/config.ini
parser = get_config_parser()
# settings.ini
par = get_settings_parser()

# CONSTANTS

MAX_INPUT_LENGTH = 1100

GUILD_SETTINGS_DEFAULT = {
    # Guild name
    "name": "",
    # Owner ID
    "owner": "",
    # Booleans (0/1) for filter settings and sleep state
    "filterwords": 0,
    "filterspam": 0,
    "filterinvite": 0,
    "sleeping": 0,
    # Notification settings
    "welcomemsg": None,
    "kickmsg": None,
    "banmsg": None,
    "leavemsg": None,
    # Log channel ID
    "logchannel": None,
    # Guild prefix
    "prefix": str(parser.get("Servers", "defaultprefix")),
    # Default channel ID
    "dchan": None,
    # Current language
    "lang": "en",
}

# Decorator utility for input validation


def security_error(fn, args, kwargs):
    raise SecurityError("WARNING: function: {}\nParameters: {}, {}".format(fn.__name__, args, kwargs))


def validate_input(fn):
    def wrapper(self, *args, **kwargs):
        if max([len(str(a)) for a in args]) > MAX_INPUT_LENGTH:
            security_error(fn, args, kwargs)

        for k, v in kwargs.items():
            if (len(str(k)) > MAX_INPUT_LENGTH) or (len(str(v)) > MAX_INPUT_LENGTH):
                security_error(fn, args, kwargs)

        # If no filters need to be applied, do everything normally
        return fn(self, *args, **kwargs)

    return wrapper

# RedisServerHandler is a singleton, --> only one instance
# Singleton imported from utils


class ServerHandler:
    @staticmethod
    def get_redis_data_credentials() -> tuple:
        if par.get("Redis", "setup") == "environment":
            redis_ip = os.environ["REDIS_HOST"]
            redis_port = os.environ["REDIS_PORT"]
            redis_pass = os.environ["REDIS_PASS"]
        else:
            redis_ip = par.get("Redis", "ip", fallback="localhost")
            redis_port = par.get("Redis", "port", fallback=6379)
            redis_pass = par.get("Redis", "password", fallback=None)

        return redis_ip, redis_port, redis_pass

    @staticmethod
    def get_redis_cache_credentials() -> tuple:
        if par.get("RedisCache", "setup") == "environment":
            redis_ip = os.environ["REDIS_CACHE_HOST"]
            redis_port = os.environ["REDIS_CACHE_PORT"]
            redis_pass = os.environ["REDIS_CACHE_PASS"]
        else:
            redis_ip = par.get("RedisCache", "ip", fallback="localhost")
            redis_port = par.get("RedisCache", "port", fallback=6380)
            redis_pass = par.get("RedisCache", "password", fallback=None)

        return redis_ip, redis_port, redis_pass

    @classmethod
    def get_handler(cls, loop) -> "RedisServerHandler":
        # Factory method
        redis_ip, redis_port, redis_pass = cls.get_redis_data_credentials()
        return RedisServerHandler(loop, redis_ip, redis_port, redis_pass)

    @staticmethod
    def get_cache_handler() -> "RedisCacheHandler":
        return RedisCacheHandler()

    @staticmethod
    def make_pool(ip, port, password, **kwargs):
        log.info("Created ConnectionPool for {}:{}".format(ip, port))
        return redis.ConnectionPool(host=ip, port=port, password=password, **kwargs)

    # Permission checker
    @staticmethod
    def has_role(member: Member, role_name: str):
        if not isinstance(member, Member):
            raise TypeError("expected Member, got {}".format(type(member).__name__))

        for role in member.roles:
            if role.name == role_name:
                return True

        return False

    @staticmethod
    def is_bot_owner(user_id: int):
        return user_id == int(par.get("Settings", "ownerid"))

    @staticmethod
    def is_server_owner(user_id: int, server: Guild):
        return user_id == server.owner.id

    def is_admin(self, member: Member, guild: Guild):
        # Changed in 3.7
        # Having Nano Admin allows access to Nano Mod commands as well
        bo = self.is_bot_owner(member.id)
        so = self.is_server_owner(member.id, guild)
        im = self.has_role(member, "Nano Mod")
        ia = self.has_role(member, "Nano Admin")

        return bo or so or ia or im

    def is_mod(self, member: Member, guild: Guild):
        bo = self.is_bot_owner(member.id)
        so = self.is_server_owner(member.id, guild)
        im = self.has_role(member, "Nano Mod")

        return bo or so or im


# Everything regarding RedisServerHandler below
# Careful when converting data, this was changed (see converter.py for implementation)
WORDFILTER_SETTING = "wordfilter"
SPAMFILTER_SETTING = "spamfilter"
INVITEFILTER_SETTING = "invitefilter"

mod_settings_map = {
    "word filter": WORDFILTER_SETTING,
    "filter words": WORDFILTER_SETTING,
    "filterwords": WORDFILTER_SETTING,
    "wordfilter": WORDFILTER_SETTING,

    "spam filter": SPAMFILTER_SETTING,
    "filter spam": SPAMFILTER_SETTING,
    "spamfilter": SPAMFILTER_SETTING,
    "filterspam": SPAMFILTER_SETTING,

    "invite filter": INVITEFILTER_SETTING,
    "filterinvite": INVITEFILTER_SETTING,
    "filterinvites": INVITEFILTER_SETTING,
    "invitefilter": INVITEFILTER_SETTING,
}

# IMPORTANT
# The format for saving server data is => server:id_here
# For commands => commands:id_here
# For mutes => mutes:id_here
# For blacklist => blacklist:id_here
# For selfroles => sr:


class RedisServerHandler(ServerHandler, metaclass=Singleton):
    __slots__ = ("_redis", "redis", "pool")

    def __init__(self, loop, redis_ip, redis_port, redis_password):
        super().__init__()

        self.pool = None
        self.redis = None
        self.loop = loop

        self.pool = self.make_pool(redis_ip, redis_port, redis_password, db=0)
        self.redis = redis.StrictRedis(connection_pool=self.pool)

        self.verify_connection(redis_ip, redis_port, redis_password)

    def verify_connection(self, redis_ip, redis_port, redis_password):
        try:
            self.redis.ping()
        except redis.ConnectionError:
            log.error("Could not connect to redis! Check settings.ini and your redis server")
            log.error("Retrying in 3 sec...")

            # Must be blocking
            time.sleep(3)
            self.verify_connection(redis_ip, redis_port, redis_password)


        log.info("Connected to Redis database")

    def bg_save(self):
        return bool(self.redis.bgsave() == b"OK")

    # SERVER SETUPS
    @staticmethod
    def _default_guild_data(guild):
        # These are server defaults
        s_data = GUILD_SETTINGS_DEFAULT.copy()
        s_data["owner"] = guild.owner.id
        s_data["name"] = guild.name

        # Remove entries with None
        return {a: b for a, b in s_data.items() if b is not None}

    def server_setup(self, guild: Guild):
        # These are server defaults
        s_data = self._default_guild_data(guild)

        sid = "server:{}".format(guild.id)

        self.redis.hmset(sid, s_data)
        # commands:id, mutes:id, blacklist:id and sr:id are created automatically when needed

        log.info("New server: {}".format(guild.name))

    def reset_server(self, guild: Guild):
        server_data = self._default_guild_data(guild)
        sid = "server:{}".format(guild.id)

        self.redis.delete(sid)
        self.redis.hmset(sid, server_data)

        log.info("Guild reset: {}".format(guild.name))

    def server_exists(self, server_id: int) -> bool:
        return bool(self.redis.exists("server:{}".format(server_id)))

    def auto_setup_server(self, server: Guild):
        # shortcut for checking sever existence
        if not self.server_exists(server.id):
            self.server_setup(server)

    def get_server_data(self, server) -> dict:
        # NOTE: HGETALL returns a dict with binary keys and values!
        base = decode(self.redis.hgetall("server:{}".format(server.id)))
        cmd_list = self.get_custom_commands(server)
        bl = self.get_blacklists(server)
        mutes = self.get_mute_list(server)

        data = decode(base)
        data["commands"] = cmd_list
        data["blacklist"] = bl
        data["mutes"] = mutes

        return data

    # GENERAL USE: moderation settings, server vars
    # TODO investigate uses
    def get_var(self, server_id: int, key: str):
        # If value is in json, it will be a json-encoded string and not parsed
        return decode(self.redis.hget("server:{}".format(server_id), key))

    @validate_input
    def update_var(self, server_id: int, key: str, value: str) -> bool:
        return bin2bool(self.redis.hset("server:{}".format(server_id), key, value))

    @validate_input
    def update_moderation_settings(self, server_id: int, key: str, value: bool) -> bool:
        if key not in mod_settings_map.keys():
            raise TypeError("invalid moderation setting: {}".format(key))

        return bin2bool(self.redis.hset("server:{}".format(server_id), mod_settings_map.get(key), value))

    def check_server_vars(self, server: Guild):
        try:
            sid = "server:{}".format(server.id)

            if int(decode(self.redis.hget(sid, "owner"))) != server.owner.id:
                self.redis.hset(sid, "owner", server.owner.id)

            if decode(self.redis.hget(sid, "name")) != str(server.name):
                self.redis.hset(sid, "name", server.name)
        except AttributeError:
            pass

    def check_old_servers(self, current_servers: list):
        servers = ["server:" + str(s_id) for s_id in current_servers]
        redis_servers = [decode(a) for a in self.redis.scan_iter(match="server:*")]

        # Filter - only remove server that nano is not part of anymore
        removed_servers = set(redis_servers) - set(servers)

        # Delete every old server
        for rem_serv in removed_servers:
            self.delete_server(rem_serv.strip("server:"))

        log.info("Removed {} old servers.".format(len(removed_servers)))

    def delete_server(self, server_id: int):
        self.redis.delete("commands:{}".format(server_id))
        self.redis.delete("blacklist:{}".format(server_id))
        self.redis.delete("mutes:{}".format(server_id))
        self.redis.delete("server:{}".format(server_id))
        self.redis.delete("voting:{}".format(server_id))
        self.redis.delete("sr:{}".format(server_id))

        log.info("Deleted server: {}".format(server_id))

    # COMMANDS
    @validate_input
    def set_command(self, server: Guild, trigger: str, response: str) -> bool:
        if len(trigger) > 80:
            return False

        return self.redis.hset("commands:{}".format(server.id), trigger, response)

    def remove_command(self, server: Guild, trigger: str) -> bool:
        return bin2bool(self.redis.hdel("commands:{}".format(server.id), trigger))

    def get_custom_commands(self, server_id: int) -> dict:
        return decode(self.redis.hgetall("commands:{}".format(server_id))) or {}

    def get_custom_commands_keys(self, server_id: int) -> list:
        return decode(self.redis.hkeys("commands:{}".format(server_id))) or []

    def get_custom_command_by_key(self, server_id: int, key: str) -> str:
        return decode(self.redis.hget("commands:{}".format(server_id), key))

    def get_command_amount(self, server_id: int) -> int:
        return decode(self.redis.hlen("commands:{}".format(server_id)))

    def custom_command_exists(self, server_id: int, trigger: str):
        return self.redis.hexists("commands:{}".format(server_id), trigger)

    # CHANNEL BLACKLIST
    @validate_input
    def add_channel_blacklist(self, server_id: int, channel_id: int):
        return bool(self.redis.sadd("blacklist:{}".format(server_id), channel_id))

    @validate_input
    def remove_channel_blacklist(self, server_id: int, channel_id: int):
        return bool(self.redis.srem("blacklist:{}".format(server_id), channel_id))

    def is_blacklisted(self, server_id, channel_id):
        return self.redis.sismember("blacklist:{}".format(server_id), channel_id)

    def get_blacklists(self, server_id):
        serv = "blacklist:{}".format(server_id)
        return list(decode(self.redis.smembers(serv)) or [])

    # PREFIX
    def get_prefix(self, server: Guild) -> str:
        return decode(self.redis.hget("server:{}".format(server.id), "prefix"))

    @validate_input
    def change_prefix(self, server, prefix):
        self.redis.hset("server:{}".format(server.id), "prefix", prefix)

    # MODERATION
    def has_spam_filter(self, server):
        return decode(self.redis.hget("server:{}".format(server.id), SPAMFILTER_SETTING)) is True

    def has_word_filter(self, server):
        return decode(self.redis.hget("server:{}".format(server.id), WORDFILTER_SETTING)) is True

    def has_invite_filter(self, server):
        return decode(self.redis.hget("server:{}".format(server.id), INVITEFILTER_SETTING)) is True

    def get_log_channel(self, server):
        return decode(self.redis.hget("server:{}".format(server.id), "logchannel"))

    def get_defaultchannel(self, server_id):
        return decode(self.redis.hget("server:{}".format(server_id), "dchan"))

    @validate_input
    def set_defaultchannel(self, server, channel_id):
        self.redis.hset("server:{}".format(server.id), "dchan", channel_id)

    # SETTINGS
    @validate_input
    def set_custom_channel(self, guild_id, var_name, value):
        if var_name not in ["logchannel", "dchan"]:
            raise TypeError("invalid channel type")

        if value is not None:
            return bin2bool(self.redis.hset("server:{}".format(guild_id), var_name, value))
        else:
            return self.redis.hdel("server:{}".format(guild_id), var_name)

    @validate_input
    def set_custom_event_message(self, guild_id, var_name, value):
        if var_name not in ["welcomemsg", "banmsg", "kickmsg", "leavemsg"]:
            raise TypeError("invalid event type")

        if value is not None:
            return bin2bool(self.redis.hset("server:{}".format(guild_id), var_name, value))
        else:
            return self.redis.hdel("server:{}".format(guild_id), var_name)

    # SLEEPING
    def is_sleeping(self, server_id):
        return decode(self.redis.hget("server:{}".format(server_id), "sleeping"))

    @validate_input
    def set_sleeping(self, server, bool_var):
        self.redis.hset("server:{}".format(server.id), "sleeping", bool(bool_var))

    # MUTING
    @validate_input
    def mute(self, server, user_id):
        serv = "mutes:{}".format(server.id)
        return bool(self.redis.sadd(serv, user_id))

    @validate_input
    def unmute(self, member_id, server_id):
        serv = "mutes:{}".format(server_id)
        return bool(self.redis.srem(serv, member_id))

    def is_muted(self, server, user_id):
        serv = "mutes:{}".format(server.id, user_id)
        return bool(self.redis.sismember(serv, user_id))

    def get_mute_list(self, server):
        serv = "mutes:{}".format(server.id)
        return list(decode(self.redis.smembers(serv)) or [])

    # LANGUAGES
    @validate_input
    def set_lang(self, server_id, language):
        self.redis.hset("server:{}".format(server_id), "lang", language)

    def get_lang(self, server_id):
        return decode(self.redis.hget("server:{}".format(server_id), "lang"))

    # SELFROLES
    def get_selfroles(self, server_id):
        return decode(self.redis.smembers("sr:{}".format(server_id)))

    @validate_input
    def add_selfrole(self, server_id, role_name):
        return bin2bool(self.redis.sadd("sr:{}".format(server_id), role_name))

    @validate_input
    def remove_selfrole(self, server_id, role_name):
        return bin2bool(self.redis.srem("sr:{}".format(server_id), role_name))

    def is_selfrole(self, server_id, role_name):
        return bin2bool(self.redis.sismember("sr:{}".format(server_id), role_name))

    # Special debug methods
    def db_info(self, section=None):
        return decode(self.redis.info(section=section))

    def db_size(self):
        return int(self.redis.dbsize())

    # Plugin storage system
    def get_plugin_data_manager(self, namespace, *args, **kwargs) -> "RedisPluginDataManager":
        return RedisPluginDataManager(self.pool, namespace, *args, **kwargs)

    def _get_redis_instance(self):
        return self.redis


class RedisPluginDataManager:
    def __init__(self, pool, namespace=None, *_, **__):
        self.namespace = namespace
        self.redis = redis.StrictRedis(connection_pool=pool)

        log.info("New plugin namespace registered: {}".format(self.namespace or "(no namespace)"))

    def _make_key(self, name):
        if not self.namespace:
            return name

        # Returns a hash name formatted with the namespace
        return "{}:{}".format(self.namespace, name)

    def set(self, key, val, **kwargs):
        return decode(self.redis.set(self._make_key(key), val, **kwargs))

    def get(self, key):
        return decode(self.redis.get(self._make_key(key)))

    def hget(self, name, field, use_namespace=True):
        return decode(self.redis.hget(self._make_key(name) if use_namespace else name, field))

    def hgetall(self, name, use_namespace=True):
        return decode(self.redis.hgetall(self._make_key(name) if use_namespace else name))

    def hdel(self, name, field):
        return decode(self.redis.hdel(self._make_key(name), field))

    def hmset(self, name, payload):
        return self.redis.hmset(self._make_key(name), payload)

    def hset(self, name, field, value):
        return decode(self.redis.hset(self._make_key(name), field, value))

    def hexists(self, name, field):
        return self.redis.hexists(name, field)

    def exists(self, name, use_namespace=True):
        return self.redis.exists(self._make_key(name) if use_namespace else name)

    def delete(self, name, use_namespace=True):
        return self.redis.delete(self._make_key(name) if use_namespace else name)

    def scan(self, cursor, use_namespace=True, match=None, **kwargs):
        match = self._make_key(match) if use_namespace else match
        return self.redis.scan(cursor, match=match, **kwargs)

    def sscan(self, name, cursor, use_namespace=True, match=None, **kwargs):
        match = self._make_key(match) if use_namespace else match
        return self.redis.sscan(name, cursor, match=match, **kwargs)

    def scan_iter(self, match, use_namespace=True):
        match = self._make_key(match) if use_namespace else match
        return [a.decode() for a in self.redis.scan_iter(match)]

    def sscan_iter(self, name, match=None, use_namespace=True):
        name = self._make_key(name) if use_namespace else name
        return [a.decode() for a in self.redis.sscan_iter(name, match)]

    def lpush(self, key, value):
        return self.redis.lpush(self._make_key(key), value)

    def lrange(self, key, from_key=0, to_key=-1):
        return decode(self.redis.lrange(self._make_key(key), from_key, to_key))

    def lrem(self, key, value, count=1):
        return decode(self.redis.lrem(self._make_key(key), count, value))

    def lpop(self, key):
        return decode(self.redis.lpop(self._make_key(key)))

    def sadd(self, name, *values):
        return self.redis.sadd(self._make_key(name), *values)

    def srandmember(self, name, amount=1):
        return decode(self.redis.srandmember(self._make_key(name), amount))

    def scard(self, name):
        return self.redis.scard(self._make_key(name))

    def pipeline(self, **options):
        return self.redis.pipeline(**options)

    def expire(self, name, time):
        return self.redis.expire(name, int(time))

    def ttl(self, name):
        return decode(self.redis.ttl(name))


# Singleton

class RedisCacheHandler(RedisPluginDataManager, ServerHandler, metaclass=Singleton):
    def __init__(self):
        redis_ip, redis_port, redis_pass = self.get_redis_cache_credentials()
        self.pool = self.make_pool(redis_ip, redis_port, redis_pass, db=0)

        super().__init__(self.pool)

    def get_plugin_data_manager(self, namespace):
        return RedisPluginDataManager(self.pool, namespace)
