from inspect import isfunction
from src.ui.model.annotations.get_methods import get_methods
from src.ui.model.annotations.get_type_annotation import AnnotationReader
from src.ui.model.prop_dict import PropDict


def get_sections(obj: type):
    props = PropDict()
    methods = get_methods(obj, stop_class=object)
    for k, f in methods.items():
        if not isfunction(f) or "section" not in AnnotationReader(f):
            continue
        section = AnnotationReader(f).section

        if k == "__init__":
            props = props.merge(section.props)
        else:
            props = props.merge({k: section})
    return props
