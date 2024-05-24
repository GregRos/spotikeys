from src.client.ui.shadow.model.props.from_type.get_annotation_name import (
    get_annotation_name,
)


from typing import Type


def get_inner_type_value(ty: Type):
    t = ty
    while t is not None:
        annotation_name = get_annotation_name(t)
        if annotation_name in ("Annotated", "NotRequired", "Unpack"):
            t = t.__args__[0]  # type: Type
        else:
            return t
