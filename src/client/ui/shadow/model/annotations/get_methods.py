from inspect import isfunction


def get_methods(cls, stop_class=object):
    def iter_method(cls):
        for attr_name in vars(cls):
            attr = getattr(cls, attr_name)
            if isfunction(attr):
                yield attr_name, attr

        for base_class in cls.__mro__[1:]:
            if base_class == stop_class:
                break
            yield from iter_method(base_class)

    result = {}
    for name, method in iter_method(cls):
        if name not in result:
            result[name] = method

    return result
