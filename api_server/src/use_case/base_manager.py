from src.exceptions import IntMustBePositive, ValidationError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.handles import Handles


class BaseManager:

    def __init__(self, name, repository, abstract_entity, not_found_exception):
        self.name = name
        self.repository = repository
        self.abstract_entity = abstract_entity
        self.not_found_exception = not_found_exception

    @log_call
    @auto_raise
    def search(self, ctx, limit=None, offset=None, terms=None, filter_=None) -> (list, int):
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        f = Handles.methods(self.repository)[Handles.SEARCH]

        result, count = f(self.repository, ctx, limit=limit,
                          offset=offset,
                          terms=terms,
                          filter_=filter_)

        return result, count

    @log_call
    @auto_raise
    def get_by_id(self, ctx, **kwargs):
        if self.name + '_id' not in kwargs:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        object_id = kwargs[self.name + '_id']

        f = Handles.methods(self.repository)[Handles.SEARCH]

        result, _ = f(self.repository, ctx,
                      filter_=self.abstract_entity(id=object_id))
        if not result:
            raise self.not_found_exception(object_id)

        return next(iter(result), None)

    @log_call
    @auto_raise
    def update_or_create(self, ctx, obj, **kwargs):
        if self.name + '_id' not in kwargs:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        current_object = self.get_by_id(ctx, **kwargs)
        if current_object is None:
            f = Handles.methods(self.repository)[Handles.CREATE]
            new_object = f(self.repository, ctx, obj)
            return new_object, True
        else:
            return self.partially_update(ctx, obj, override=True, **kwargs), False

    @log_call
    @auto_raise
    def partially_update(self, ctx, obj, override=False, **kwargs):
        if self.name + '_id' not in kwargs:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        object_id = kwargs[self.name + '_id']
        obj.id = object_id

        f = Handles.methods(self.repository)[Handles.UPDATE]
        return f(self.repository, ctx, obj, override=override)

    @log_call
    @auto_raise
    def delete(self, ctx, **kwargs):
        if self.name + '_id' not in kwargs:
            raise ValidationError('Parameter ' + self.name + '_id is required')

        object_id = kwargs[self.name + '_id']

        f = Handles.methods(self.repository)[Handles.DELETE]
        f(self.repository, ctx, object_id)
