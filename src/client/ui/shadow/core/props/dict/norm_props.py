from src.client.ui.shadow.core.props.single.norm_prop import norm_prop
from src.client.ui.shadow.core.props.single.just_value import JustValue
from src.client.ui.shadow.core.props.single.prop_def import PropDef
from src.client.ui.shadow.core.props.single.prop_value import PropValue


from collections.abc import Mapping


def norm_props(
    dict_a: Mapping[str, PropValue | PropDef | JustValue] | None = None,
    dict_b: Mapping[str, PropValue | PropDef | JustValue] | None = None,
) -> dict[str, PropValue | PropDef | JustValue]:
    dict_a = dict_a or {}
    dict_b = dict_b or {}
    all_props = {
        k: norm_prop(dict_a.get(k), dict_b.get(k))
        for k in dict_a.keys() | dict_b.keys()
    }
    return all_props
