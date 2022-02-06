import pinject
import abc

from src.interface_adapter.http_api.default import DefaultHandler

from src.use_case import managers
from src.interface_adapter.http_api import handlers
from src.interface_adapter.sql import repositories as sql_repositories
from src.interface_adapter.elasticsearch import ElasticSearchRepository
from src.interface_adapter.snmp import SwitchSNMPNetworkManager


from src.interface_adapter.sql.ip_allocator import IPSQLAllocator
from src.interface_adapter.sql.vlan_repository import VLANSQLRepository

from src.use_case.crud_manager import CRUDManager
from src.use_case.vlan_manager import VlanManager
from src.use_case.interface.crud_repository import CRUDRepository

class BindingSpec(pinject.BindingSpec):
    def __init__(self, configuration, testing) -> None:
        super().__init__()
        self.configration = configuration
        self.testing = testing
    def configure(self, bind):
        bind('configuration', to_instance=self.configration)
        bind('gitlab_conf', to_instance=self.configration.GITLAB_CONF)
        bind('testing', to_instance=self.testing)



_global = sql_repositories+managers+handlers+[SwitchSNMPNetworkManager, ElasticSearchRepository]

_base_interfaces = [
    abc.ABC,
    CRUDManager,
    CRUDRepository,
    DefaultHandler,
    object
]

def get_base_class(cls):
    print(cls.__name__, ": ", set(_base_interfaces)&set(cls.__bases__), " --- ", type(cls))
    if len(cls.__bases__) == 0 or set(_base_interfaces)&set(cls.__bases__):
        return cls
    return get_base_class(cls.__bases__[0])

_class_name_to_abstract = {
    cls.__name__: get_base_class(cls) for cls in _global
}

def get_arg_names(class_name):
    if class_name in _class_name_to_abstract:
        class_name = _class_name_to_abstract[class_name].__name__
    return pinject.bindings.default_get_arg_names_from_class_name(class_name)

def get_obj_graph(configuration, testing):
    return pinject.new_object_graph(
        modules=None,
        binding_specs=[BindingSpec(configuration, testing)],
        classes=_global,
        get_arg_names_from_class_name=get_arg_names
    )