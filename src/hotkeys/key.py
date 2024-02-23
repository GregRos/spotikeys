from src.hotkeys.labels import key_labels


class Key:
    def __init__(self, key_id: str):
        self.id = key_id

    @property
    def label(self):
        return key_labels.get(self.id, self.id)

    def __str__(self):
        return f"{self.label} ({self.id})"


class ModifiedKey:
    def __init__(self, base: Key, modifier: Key):
        self.base = base
        self.modifier = modifier

    @property
    def label(self):
        return f"{self.modifier.label} + {self.base.label}"

    def __str__(self):
        return f"{self.modifier} + {self.base}"
