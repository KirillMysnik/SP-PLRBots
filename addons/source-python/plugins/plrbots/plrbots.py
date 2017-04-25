# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from enum import IntEnum
import random

# Source.Python
from core import PLATFORM
from cvars import ConVar
from engines.server import execute_server_command
from entities.entity import Entity
from events import Event
from filters.entities import EntityIter
from filters.players import PlayerIter
from listeners import OnEntityOutput
import memory
from memory import make_object
from memory.hooks import PostHook, PreHook
from messages import SayText2
from players.dictionary import PlayerDictionary
from players.entity import Player
from players.teams import teams_by_number

# PLRBots
from .core.cvars import config_manager
from .core.memory import server_tools, TFBotScenarioMonitor, TFGameRules
from .core.strings import COLOR_SCHEME, common_strings


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def broadcast(message):
    message = message.tokenized(**message.tokens, **COLOR_SCHEME)
    message = common_strings['chat_base'].tokenized(
        message=message, **COLOR_SCHEME)

    SayText2(message).send()


def find_trains(cp_names):
    for train_watcher in EntityIter('team_train_watcher'):
        for cp_index in range(8):
            key = "linked_cp_{}".format(cp_index + 1)
            cp_name = get_key_value_string_t(train_watcher, key)
            if cp_name in cp_names:
                break
        else:
            continue

        team = train_watcher.get_key_value_int('TeamNum')
        if team == 0:
            train_watchers_by_team[ATTACKING_TEAM] = train_watcher.inthandle
            train_watchers_by_team[DEFENDING_TEAM] = train_watcher.inthandle
        elif team in (ATTACKING_TEAM, DEFENDING_TEAM):
            train_watchers_by_team[team] = train_watcher.inthandle


def get_key_value_string_t(entity, key):
    result = memory.alloc(KEY_VALUE_SIZE)
    fl = server_tools.get_key_value(entity, key, result, KEY_VALUE_SIZE)
    if not fl:
        return None

    return result.get_string_pointer()


def get_player_class(player):
    return player.get_property_uchar("m_PlayerClass.m_iClass")


def set_player_class(player, player_class):
    player.set_property_uchar("m_PlayerClass.m_iClass", player_class)
    player.set_property_uchar("m_Shared.m_iDesiredPlayerClass", player_class)


def change_to_random_class(player):
    class_chances = {key: 1 for key in range(1, 10)}
    for player_ in PlayerIter(teams_by_number[player.team]):
        player_class = get_player_class(player_)
        if player_class not in class_chances:
            continue

        class_chances[player_class] *= 0.5

    x = random.random() * sum(class_chances.values())
    full_chance = 0
    for player_class, chance in class_chances.items():
        full_chance += chance
        if x < full_chance:
            break

    set_player_class(player, player_class)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
KEY_VALUE_SIZE = 1024
ATTACKING_TEAM = 3
DEFENDING_TEAM = 2

PROFESSION_CVAR_NAMES = {
    1: 'scout_push_chance',
    2: 'sniper_push_chance',
    3: 'soldier_push_chance',
    4: 'demo_push_chance',
    5: 'medic_push_chance',
    6: 'heavy_push_chance',
    7: 'pyro_push_chance',
    8: 'spy_push_chance',
    9: 'engineer_push_chance',
}

cvar_restartgame = ConVar('mp_restartgame')
cvar_bot_quota = ConVar('tf_bot_quota')

bot_quota = None
train_watchers_by_team = {}
bot_professions = PlayerDictionary(lambda index: BotProfession.BLOCK)
temp_teams = PlayerDictionary(lambda index: 0)
game_rules = None


# =============================================================================
# >> CLASSES
# =============================================================================
class BotProfession(IntEnum):
    BLOCK = 0
    PUSH = 1


# =============================================================================
# >> EVENTS
# =============================================================================
@Event('player_death')
def on_player_death(game_event):
    player = Player.from_userid(game_event['userid'])
    if player.steamid != "BOT":
        return

    if player.team not in (ATTACKING_TEAM, DEFENDING_TEAM):
        return

    if random.random() >= config_manager['class_change_chance']:
        return

    change_to_random_class(player)


@Event('player_spawn')
def on_player_spawn(game_event):
    player = Player.from_userid(game_event['userid'])
    if player.steamid != "BOT":
        return

    player_class = get_player_class(player)
    if player_class not in PROFESSION_CVAR_NAMES:
        return

    chance_to_push = config_manager[PROFESSION_CVAR_NAMES[player_class]]
    if random.random() < chance_to_push:
        bot_professions[player.index] = BotProfession.PUSH
    else:
        bot_professions[player.index] = BotProfession.BLOCK


@Event('teamplay_round_active')
def on_round_start(game_event):
    if game_rules is None:
        return

    if not config_manager['force_disable_setup_time']:
        return

    game_rules.set_setup(False)


# =============================================================================
# >> HOOKS
# =============================================================================
if PLATFORM == "windows":

    @PreHook(TFGameRules.get_payload_to_push)
    def pre_get_payload_to_push(args):
        team = args[2]
        if team not in train_watchers_by_team:
            return

        train_watcher_handle = train_watchers_by_team[team]
        args[1].set_uint(train_watcher_handle)
        return args[1]


    @PreHook(TFGameRules.get_payload_to_block)
    def pre_get_payload_to_block(args):
        team = args[2]
        if team not in train_watchers_by_team:
            return

        train_watcher_handle = train_watchers_by_team[
            ATTACKING_TEAM + DEFENDING_TEAM - team]
        args[1].set_uint(train_watcher_handle)
        return args[1]

else:

    @PreHook(TFGameRules.get_payload_to_push)
    def pre_get_payload_to_push(args):
        team = args[2]
        if team not in train_watchers_by_team:
            return

        train_watcher_handle = train_watchers_by_team[team]
        args[1].set_uint(train_watcher_handle)
        return False


    @PreHook(TFGameRules.get_payload_to_block)
    def pre_get_payload_to_block(args):
        team = args[2]
        if team not in train_watchers_by_team:
            return

        train_watcher_handle = train_watchers_by_team[
            ATTACKING_TEAM + DEFENDING_TEAM - team]

        args[1].set_uint(train_watcher_handle)
        return False


@PreHook(TFBotScenarioMonitor.desired_scenario_and_class_action)
def pre_desired_scenario_and_class_action(args):
    entity = make_object(Entity, args[1])
    temp_teams[entity.index] = entity.team
    if bot_professions[entity.index] == BotProfession.PUSH:
        entity.team = ATTACKING_TEAM
    else:
        entity.team = DEFENDING_TEAM


@PostHook(TFBotScenarioMonitor.desired_scenario_and_class_action)
def post_desired_scenario_and_class_action(args, ret_val):
    entity = make_object(Entity, args[1])
    entity.team = temp_teams[entity.index]


@PreHook(TFGameRules.setup_on_round_start)
def pre_tf_game_rules_init(args):
    global game_rules
    game_rules = make_object(TFGameRules, args[0])


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityOutput
def listener_on_entity_output(output_name, activator, caller, value, delay):
    if output_name != "OnStart":
        return

    if caller.classname != "team_control_point_round":
        return

    try:
        cp_names = caller.get_key_value_string('cpr_cp_names')
    except UnicodeDecodeError:
        cp_names = get_key_value_string_t(caller, 'cpr_cp_names')

    find_trains(cp_names.split(' '))

    global bot_quota
    if bot_quota is not None:
        cvar_bot_quota.set_int(bot_quota)
        bot_quota = None


# =============================================================================
# >> LOAD & UNLOAD FUNCTIONS
# =============================================================================
def load():
    # Save the bot quota
    global bot_quota
    bot_quota = cvar_bot_quota.get_int()

    # Kick all bots so that our hooks don't crash the server
    execute_server_command('tf_bot_kick', 'all')

    # Restart the round to get bots back again
    cvar_restartgame.set_int(1)

    broadcast(common_strings['loaded'])


def unload():
    # Kick all bots so that our hooks don't crash the server
    execute_server_command('tf_bot_kick', 'all')

    broadcast(common_strings['unloaded'])
