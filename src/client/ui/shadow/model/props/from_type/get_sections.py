from inspect import isfunction
from src.client.ui.shadow.model.props.dict.props_dict import PropsDict
from src.client.ui.shadow.model.props.from_type.get_type_annotation import (
    AnnotationReader,
)


def get_methods(cls, stop_class=object):
    for attr_name in vars(cls):
        attr = getattr(cls, attr_name)
        if isfunction(attr):
            yield attr_name, attr

    for base_class in cls.__mro__[1:]:
        if base_class == stop_class:
            break
        yield from get_methods(base_class, stop_class=stop_class)


def get_sections(obj: type):
    props = PropsDict()
    methods = dict(get_methods(obj, stop_class=object))
    for k, f in methods.items():
        if not isfunction(f) or "section" not in AnnotationReader(f):
            continue
        section = AnnotationReader(f).section

        if k == "__init__":
            props = props.merge(section.props)
        else:
            props = props.merge({k: section})
    return props
