from typing import TYPE_CHECKING, Any, Callable


if TYPE_CHECKING:
    from src.ui.model.prop_dict import PSection
    from src.ui.model.prop_dict import PDict
    from src.ui.model.prop import Prop


class AnnotationReader:
    def __init__(self, target: Any) -> None:
        self._target = target

    def get_annotation(self, name: str) -> Any:
        x = self._target.__annotations__[name]
        assert x is not None, f"Annotation {name} not found"
        return x

    def set_annotation(self, name: str, value: Any) -> None:
        self._target.__annotations__[name] = value

    def __contains__(self, name: str) -> bool:
        return name in self._target.__annotations__

    @property
    def prop(self) -> "Prop":
        return self.get_annotation("prop")

    @prop.setter
    def prop(self, value: "Prop") -> None:
        self.set_annotation("prop", value)

    @property
    def section(self) -> "PSection":
        return self.get_annotation("section")

    @section.setter
    def section(self, value: "PSection") -> None:
        self.set_annotation("section", value)

    @property
    def metadata(self) -> "PSection | Prop | None":
        if "section" in self:
            return self.section
        if "prop" in self:
            return self.prop
        return None
