# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
import core
from core import PLATFORM
import memory
from memory import (
    CallingConvention, Convention, DataType, make_object, Register)
from memory.manager import TypeManager

# PLRBots
from .paths import PLRBOTS_DATA_PATH


# =============================================================================
# >> CALLING CONVENTIONS
# =============================================================================
class _GetPayloadConvention(CallingConvention):
    def get_registers(self):
        return [Register.ESP]

    def get_pop_size(self):
        return 4

    def get_argument_ptr(self, index, registers):
        if index == 0:
            return registers.esp.address.get_pointer() + 8

        if index == 1:
            return registers.esp.address.get_pointer() + 4

        if index == 2:
            return registers.esp.address.get_pointer() + 12

        raise IndexError

    def argument_ptr_changed(self, index, registers, arg_ptr):
        pass

    def get_return_ptr(self, registers):
        pass

    def return_ptr_changed(self, registers, return_ptr):
        pass


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
MEMORY_PATH = PLRBOTS_DATA_PATH / 'memory'
server = memory.find_binary('server')

if PLATFORM == "windows":
    _server_tools_interface = core.get_interface(
        "tf/bin/server.dll", 'VSERVERTOOLS002')
else:
    _server_tools_interface = core.get_interface(
        "tf/bin/server_srv.so", 'VSERVERTOOLS002')


# =============================================================================
# >> CLASSES
# =============================================================================
class PLRTypeManager(TypeManager):
    def function(
            self, identifier, args=(), return_type=DataType.VOID,
            convention=Convention.THISCALL, doc=None):

        if convention == Convention.CUSTOM:
            convention = _GetPayloadConvention

        return super().function(identifier, args, return_type, convention, doc)

payload_type_manager = PLRTypeManager()
type_manager = TypeManager()


# CServerTools
ServerTools = type_manager.create_type_from_file(
    'CServerTools',  MEMORY_PATH / 'CServerTools.ini')

server_tools = make_object(ServerTools, _server_tools_interface)

# CTFBotScenarioMonitor
TFBotScenarioMonitor = type_manager.create_type_from_file(
    'CTFBotScenarioMonitor', MEMORY_PATH / 'CTFBotScenarioMonitor.ini')

# CTFGameRules
TFGameRules = payload_type_manager.create_type_from_file(
    'CTFGameRules', MEMORY_PATH / 'CTFGameRules.ini')
