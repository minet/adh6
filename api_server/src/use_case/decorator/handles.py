class Method:
    def __init__(self, f):
        self._function = f

    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)


class Handles:

    class SEARCH(Method):
        pass

    class CREATE(Method):
        pass

    class UPDATE(Method):
        pass

    class DELETE(Method):
        pass

    @classmethod
    def methods(cls, subject):
        def g():
            for name in dir(subject):
                method = getattr(subject, name)
                print(method, type(method))
                if isinstance(method, Method):
                    yield type(method), method

        return {method_name: method for method_name, method in g()}