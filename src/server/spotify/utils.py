def not_none[T](x: T | None) -> T:
    if x is None:
        raise TypeError("Expected non-None value")
    return x
