from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.exceptions import IntMustBePositive, ValidationError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.decorator.auth import auth_required, Roles
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.interface.crud_repository import CRUDRepository


class CRUDManager:

    def __init__(self, name, repository: CRUDRepository, abstract_entity, not_found_exception):
        self.name = name
        self.repository = repository
        self.abstract_entity = abstract_entity
        self.not_found_exception = not_found_exception

    # The default behavior is to assume the user does not have the required permissions
    def default_access_control_function(self, ctx, f, args, kwargs):
        return args, kwargs, False

    def search_access_control_function(self, ctx, f, args, kwargs):
        return self.default_access_control_function(ctx, f, args, kwargs)

    def get_by_id_access_control_function(self, ctx, f, args, kwargs):
        return self.default_access_control_function(ctx, f, args, kwargs)

    def update_or_create_access_control_function(self, ctx, f, args, kwargs):
        return self.default_access_control_function(ctx, f, args, kwargs)

    def partially_update_access_control_function(self, ctx, f, args, kwargs):
        return self.default_access_control_function(ctx, f, args, kwargs)

    def _delete_access_control_function(self, ctx, f, args, kwargs):
        return self.delete_access_control_function(ctx, f, args, kwargs)

    def delete_access_control_function(self, ctx, f, args, kwargs):
        return self.default_access_control_function(ctx, f, args, kwargs)

    @log_call
    @auto_raise
    @auth_required(roles=[Roles.ADH6_USER], access_control_function=search_access_control_function)
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None) -> (list, int):
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        result, count = self.repository.search_by(ctx, limit=limit,
                                                  offset=offset,
                                                  terms=terms,
                                                  filter_=filter_)

        return result, count

    @log_call
    @auto_raise
    @auth_required(roles=[Roles.ADH6_USER], access_control_function=get_by_id_access_control_function)
    def get_by_id(self, ctx, **kwargs):
        if self.name + '_id' not in kwargs or kwargs[self.name + '_id'] is None:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        object_id = kwargs[self.name + '_id']

        result, _ = self.repository.search_by(ctx,
                                              filter_=self.abstract_entity(id=object_id))
        if not result:
            raise self.not_found_exception(object_id)

        return next(iter(result), None)

    @log_call
    @auto_raise
    @auth_required(roles=[Roles.ADH6_USER], access_control_function=update_or_create_access_control_function)
    def update_or_create(self, ctx, obj, **kwargs):
        current_object = None
        if self.name + '_id' in kwargs and kwargs[self.name + '_id'] is not None:
            try:
                current_object = self.get_by_id(ctx, **kwargs)
            except:
                raise

        if current_object is None:
            new_object = self.repository.create(ctx, obj)
            return new_object, True
        else:
            return self.partially_update(ctx, obj, override=True, **kwargs)

    @log_call
    @auto_raise
    @auth_required(roles=[Roles.ADH6_USER], access_control_function=partially_update_access_control_function)
    def partially_update(self, ctx, obj, override=False, **kwargs):
        if self.name + '_id' not in kwargs or kwargs[self.name + '_id'] is None:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        object_id = kwargs[self.name + '_id']
        obj.id = object_id

        return self.repository.update(ctx, obj, override=override), False

    @log_call
    @auto_raise
    @auth_required(roles=[Roles.ADH6_USER], access_control_function=_delete_access_control_function)
    def delete(self, ctx, **kwargs):
        if self.name + '_id' not in kwargs or kwargs[self.name + '_id'] is None:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        object_id = kwargs[self.name + '_id']

        self.repository.delete(ctx, object_id)
