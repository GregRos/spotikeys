from src.commanding.commands import Command


class CommandClass(type):
    def __init__(cls, name, bases, dct, group_name: str):
        super().__init__(name, bases, dct)
        cls.group_name = group_name

    def __new__(cls, name, bases, dct, group_name: str):
        return super().__new__(cls, name, bases, dct)

    def __getattribute__(cls, key: str):
        result = super().__getattribute__(key)
        if isinstance(result, Command):
            return result.with_group(cls.group_name)
        return result
