import typing as t


def str_not_int(x: str | int) -> t.TypeGuard[str]:
    return isinstance(x, str)


def f(x: str | int) -> None:
    if str_not_int(x):
        reveal_type(x)
    else:
        ...


def g(x: str | int) -> None:
    if str_not_int(x):
        reveal_type(x)
        return
