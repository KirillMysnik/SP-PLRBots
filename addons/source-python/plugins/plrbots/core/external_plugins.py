# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from listeners import OnPluginLoaded, OnPluginUnloaded
from plugins.manager import plugin_manager


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_external_plugin_interfaces = {}


# =============================================================================
# >> CLASSES
# =============================================================================
class ExternalPluginInterface:
    def __init__(self, plugin_name):
        super().__init__()

        if plugin_name in _external_plugin_interfaces:
            raise ValueError("ExternalPluginInterface for '{}' is already "
                             "registered".format(plugin_name))

        self._plugin = plugin_manager.get_plugin_instance(plugin_name)
        _external_plugin_interfaces[plugin_name] = self

    def __getitem__(self, key):
        if self._plugin is None:
            return None

        obj = self._plugin.module
        for name in key.split('.'):
            obj = getattr(obj, name)

        return obj

    def set_plugin(self, plugin):
        self._plugin = plugin

    plugin = property(fset=set_plugin)


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnPluginLoaded
def listener_on_plugin_loaded(plugin):
    if plugin.name in _external_plugin_interfaces:
        _external_plugin_interfaces[plugin.name].plugin = plugin


@OnPluginUnloaded
def listener_on_plugin_unloaded(plugin):
    if plugin.name in _external_plugin_interfaces:
        _external_plugin_interfaces[plugin.name].plugin = None
