class Expression:

    def __init__(self, *terms):
        self._terms = terms

    def __call__(self, arguments):
        values = []
        for term in self._terms:

            if isinstance(term, property):
                if term.fget.__qualname__ not in arguments:
                    return False
                values.append(arguments[term.fget.__qualname__])
            elif isinstance(term, Expression):
                values.append(term(arguments))
            else:
                values.append(term)

        return self._operate(*values)

    def __and__(self, other):
        return BinaryExpression(self, other, operator=lambda x, y: x and y)

    def __or__(self, other):
        return BinaryExpression(self, other, operator=lambda x, y: x or y)

    def _operate(self, *values):
        raise NotImplemented

    def __repr__(self):
        ret = ""
        for term in self._terms:
            if isinstance(term, property):
                ret += term.fget.__qualname__
            elif isinstance(term, Expression):
                ret += str(term)
            else:
                ret += term
        return ret


class NestedPropertyExpression(Expression):
    def __init__(self, obj, prop):
        super().__init__()
        self.object = obj
        self.property = prop

    def __call__(self, arguments):
        if self.object.fget.__qualname__ not in arguments:
            return False
        if not hasattr(arguments[self.object.fget.__qualname__], self.property):
            return False
        return getattr(arguments[self.object.fget.__qualname__], self.property)


class BinaryExpression(Expression):
    def __init__(self, left, right, operator=None):
        super().__init__(left, right)
        self._operator = operator

    def _operate(self, left, right):
        if self._operator is None:  # Assume we're working with a simple boolean and then
            return left and right

        result = False
        try:
            result = self._operator(left, right)
        except ValueError:
            result = False

        return result

    def __repr__(self):
        return "(" + str(self._terms[0]) + str(self._operator) + str(self._terms[1]) + ")"


class TrueExpression(Expression):
    def __init__(self):
        super().__init__()

    def _operate(self, *values):
        return True

    def __repr__(self):
        return "(true)"
