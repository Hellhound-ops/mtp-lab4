"""Генераторы Фибоначчи и случайных значений для варианта 3."""

from collections.abc import Iterator
import random

from functional import integer


def fibonacci() -> Iterator[int]:
    """Среднее №5: бесконечная последовательность 0, 1, 1, 2, ..."""
    previous, current = 0, 1
    while True:
        yield previous
        previous, current = current, previous + current


def check_range(lower: int, upper: int) -> None:
    integer(lower)
    integer(upper)
    if lower > upper:
        raise ValueError("Нижняя граница больше верхней")


def random_numbers(
    lower: int, upper: int, count: int, *, seed: int | None = None,
) -> Iterator[int]:
    """Среднее №9: выдать count целых чисел в диапазоне [lower, upper]."""
    check_range(lower, upper)
    integer(count)
    if count < 0:
        raise ValueError("Количество не может быть отрицательным")
    rng = random.Random(seed)
    for _ in range(count):
        yield rng.randint(lower, upper)


def random_data(
    lower: int = 0, upper: int = 100, *, seed: int | None = None,
) -> Iterator[dict[str, int]]:
    """Повышенное №7: бесконечный поток записей с номером и значением."""
    check_range(lower, upper)
    rng = random.Random(seed)
    number = 1
    while True:
        yield {"number": number, "value": rng.randint(lower, upper)}
        number += 1
