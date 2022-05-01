# coding=utf-8
from typing import Any, Dict, List, Optional
from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractDevice, Device
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.http_api.util.serializer import deserialize_request, serialize_response
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.device_manager import DeviceManager


class DeviceHandler(DefaultHandler):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(Device, AbstractDevice, device_manager)
        self.device_manager = device_manager
    
    @with_context
    @require_sql
    @log_call
    def search(self, ctx, limit: int=DEFAULT_LIMIT, offset: int=DEFAULT_OFFSET, terms=None, filter_=None, only: Optional[List[str]]=None):
        try:
            def remove_test(entity: Dict[str, Any]) -> Dict[str, Any]:
                if only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id", "__typename"]:
                            print(k)
                            del entity[k]
                return entity

            filter_ = deserialize_request(filter_, self.abstract_entity_class)
            result, total_count = self.main_manager.search(ctx, limit=limit, offset=offset, terms=terms,
                                                           filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(remove_test, map(serialize_response, result)))
            return result, 200, headers 
        except Exception as e:
            return handle_error(ctx, e)  

    @with_context
    @require_sql
    @log_call
    def vendor_get(self, ctx, id_=None):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mac_vendor(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def device_mab_get(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.get_mab(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def device_mab_put(self, ctx, id_: int):
        """ Return the vendor associated with the given device """
        try:
            return self.device_manager.put_mab(ctx, id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)
