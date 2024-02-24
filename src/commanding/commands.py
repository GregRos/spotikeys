from __future__ import annotations

from datetime import datetime
from multiprocessing import Process, Pipe
from typing import Literal, Callable
from src.hotkeys.key import Key, ModifiedKey
from threading import Event


class Command[Code: str]:
    code: Code

    def __init__(self, command: Code, label: str):
        self.code = command
        self.label = label

    def is_command(self, command: Command[Code]):
        return self.code == command.code

    def __str__(self):
        return f"{self.label} ({self.code})"

    def to_received(self, key: Key | ModifiedKey):
        return ReceivedCommand[Code](self, key)

    def handle(self, callback: Callable[[ReceivedCommand[Code]], None]):
        return CommandHandler[Code](self, callback)


class ReceivedCommand[Code: str](Command):
    def __init__(self, command: Command, key: Key | ModifiedKey):
        super().__init__(command.code, command.label)
        self.key = key
        self.received = datetime.now()

    def __str__(self):
        return f"{self.received}: {self.key} -- {self.label} ({self.code})"


class CommandHandler[Code: str]:
    def __init__(
        self, command: Command, on_received: Callable[[ReceivedCommand[Code]], None]
    ):
        self.on_received = on_received
        self.command = command


class CommandManager[Code: str]:
    _current: ReceivedCommand[Code] | None = None
    _current_process: Process | None = None
    _pipe = Pipe()
    _handlers: dict[Code, CommandHandler[Code]] = {}

    def __init__(self, cancel_command: Command[Code]):
        self._cancel_command = cancel_command
        self._current_process = Process()

    def handles(self, command: Command[Code]):
        def decorator(callback: Callable[[ReceivedCommand[Code]], None]):
            self.add_handlers(CommandHandler[Code](command, callback))
            return callback

        return decorator

    def cancel(self):
        self._current_process.terminate()

    def receive(self, received: ReceivedCommand[Code]):
        if received.is_command(self._cancel_command):
            if not self._current:
                print(f"{received} ➔ Nothing to cancel")
                return
            print(f"{received} ➔ Cancelling {self._current}")
            self.cancel()
            return
        handler = self._handlers.get(received.code)
        if not handler:
            raise ValueError(f"No handler for {received.code}")

        if self._current:
            print(f"Received {received} while {self._current} is still being handled.")
            return

        self._current_process = Process(
            target=handler.on_received,
            args=(received,),
            daemon=True,
            name=received.code,
        )
        self._current_process.start()

    def add_handlers(self, *handlers: CommandHandler[Code]):
        for handler in handlers:
            if handler.command.code in self._handlers:
                raise ValueError(f"Handler for {handler.command} already exists")
            self._handlers[handler.command.code] = handler
