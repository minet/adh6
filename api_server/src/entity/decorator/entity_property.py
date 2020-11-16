import operator

from src.entity.util.logic import BinaryExpression, Expression, NestedPropertyExpression


class entity_property(property):

    def __eq__(self, other):
        return BinaryExpression(self, other, operator=operator.eq)

    def __ne__(self, other):
        return BinaryExpression(self, other, operator=operator.ne)

    def __lt__(self, other):
        return BinaryExpression(self, other, operator=operator.lt)

    def __le__(self, other):
        return BinaryExpression(self, other, operator=operator.le)

    def __gt__(self, other):
        return BinaryExpression(self, other, operator=operator.gt)

    def __ge__(self, other):
        return BinaryExpression(self, other, operator=operator.ge)

    def __getattr__(self, item):
        return NestedPropertyExpression(self, item)
