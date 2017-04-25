# =============================================================================
# >> IMPORTS
# =============================================================================
# Custom Package
from controlled_cvars import ControlledConfigManager, InvalidValue
from controlled_cvars.handlers import bool_handler, float_handler

# PLRBots
from ..info import info
from .strings import config_strings


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def chance_handler(cvar):
    value = float_handler(cvar)
    if 0.0 <= value <= 1.0:
        return value
    raise InvalidValue


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
config_manager = ControlledConfigManager(
    info.name + "/main", cvar_prefix='plrbots_')

config_manager.section(config_strings['section setup_time'])
config_manager.controlled_cvar(
    bool_handler,
    "force_disable_setup_time",
    default=1,
    description=config_strings['force_disable_setup_time'],
)

config_manager.section(config_strings['section class_changing'])
config_manager.controlled_cvar(
    chance_handler,
    "class_change_chance",
    default=0.2,
    description=config_strings['class_change_chance'],
)

config_manager.section(config_strings['section professions'])
config_manager.controlled_cvar(
    chance_handler,
    "scout_push_chance",
    default=1.0,
    description=config_strings['scout_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "sniper_push_chance",
    default=0.0,
    description=config_strings['sniper_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "soldier_push_chance",
    default=0.75,
    description=config_strings['soldier_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "demo_push_chance",
    default=0.5,
    description=config_strings['demo_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "medic_push_chance",
    default=0.5,
    description=config_strings['medic_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "heavy_push_chance",
    default=0.75,
    description=config_strings['heavy_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "pyro_push_chance",
    default=0.5,
    description=config_strings['pyro_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "spy_push_chance",
    default=1.0,
    description=config_strings['spy_push_chance'],
)
config_manager.controlled_cvar(
    chance_handler,
    "engineer_push_chance",
    default=0.5,
    description=config_strings['engineer_push_chance'],
)

config_manager.write()
config_manager.execute()
