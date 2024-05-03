from dataclasses import dataclass, field
from datetime import datetime
from src.client.ui.shadow.core.props.shadow_node import ShadowNode


@dataclass
class ResourceRecord[Node: ShadowNode, Resource]:
    node: Node
    resource: Resource
    created: datetime = field(default_factory=datetime.now)
