class JustValue[X]:
    __match_args__ = ("value",)

    def __init__(self, value: X):
        self.value = value
