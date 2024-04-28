from typing import Callable
from src.client.ui.framework.active_value import Disposable, Subscribable


class BindableProperty[Value]:
    _binding: Disposable

    def __init__(self, name: str, on_change: Callable[[Value], None]):
        self._name = name
        self._on_change = on_change

    def set(self, binding: Subscribable[Value]):
        if self._binding:
            self._binding.dispose()
        self._binding = binding.subscribe(self._on_change)

def bindable[Value](wrapped)