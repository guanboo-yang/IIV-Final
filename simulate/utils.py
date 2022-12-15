from random import randrange
from typing import Iterator


def next_iter(iterable: Iterator[int]) -> int | None:
    try:
        return next(iterable)
    except StopIteration:
        return None


def gen_color():
    color = ()
    while sum(color) > 300 or sum(color) < 100:
        color = randrange(256), randrange(256), randrange(256)
    return color
