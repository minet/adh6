from src.entity.decorator.entity_property import entity_property


class Expression:

    def __init__(self, *terms):
        self._terms = terms

    def __call__(self, obj):
        values = []
        for term in self._terms:
            if isinstance(term, entity_property):
                values.append(term.__get__(obj))
            elif isinstance(term, Expression):
                values.append(term(obj))
            else:
                values.append(term)

        return self._operate(*values)

    def __and__(self, other):
        return BinaryExpression(self, other, operator=lambda x, y: x and y)

    def __or__(self, other):
        return BinaryExpression(self, other, operator=lambda x, y: x or y)

    def _operate(self, *values):
        raise NotImplemented


class BinaryExpression(Expression):
    def __init__(self, left, right, operator=None):
        super().__init__(left, right)
        self._operator = operator

    def _operate(self, left, right):
        if self._operator is None:  # Assume we're working with a simple boolean and then
            return left and right

        return self._operator(left, right)
