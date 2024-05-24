from src.client.ui.shadow.model.props.from_type.get_annotation_name import (
    get_annotation_name,
)


from typing import Any, Type


def get_metadata(t: Type) -> tuple[Any, ...]:
    origin = get_annotation_name(t)
    if origin == "Annotated":
        return t.__metadata__  # type: tuple[Type, ...]
    else:
        return ()  # type: tuple[Type, ...]
