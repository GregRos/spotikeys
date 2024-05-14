from abc import ABC, abstractmethod
from numbers import Number
from typing import Any, Callable, Protocol, runtime_checkable

from functools import wraps
from typing import Any, Callable, TypeVar

from pydantic import BaseModel
from typing_extensions import Concatenate, ParamSpec
