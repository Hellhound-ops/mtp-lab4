"""Среднее №3 и повышенное №3: reduce и каррирование."""

from collections.abc import Callable, Iterable
from functools import reduce
from inspect import Parameter, signature
from typing import Any


def integer(value: int) -> int:
    """Проверить целое число, исключая логические значения."""
    if type(value) is not int:
        raise TypeError("Ожидается целое число")
    return value


def total(numbers: Iterable[int]) -> int:
    """Сложить целые числа через reduce; сумма пустого ввода равна нулю."""
    return reduce(lambda left, right: left + right, map(integer, numbers), 0)


def curry(function: Callable[..., Any]) -> Callable[[Any], Any]:
    """Преобразовать f(a, b, c) в f(a)(b)(c).

    Поддерживаются функции с одним или более обязательными позиционными
    параметрами без значений по умолчанию, *args, **kwargs и keyword-only.
    Каждый вызов полученной цепочки принимает ровно один аргумент.
    """
    if not callable(function):
        raise TypeError("Ожидается функция")
    parameters = list(signature(function).parameters.values())
    if not parameters:
        raise ValueError("У функции должен быть хотя бы один параметр")
    for parameter in parameters:
        if parameter.kind not in (
            Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD
        ) or parameter.default is not Parameter.empty:
            raise ValueError("Нужны обязательные позиционные параметры")

    def collect(arguments: tuple) -> Callable[[Any], Any]:
        def receive(value: Any) -> Any:
            collected = arguments + (value,)
            if len(collected) == len(parameters):
                return function(*collected)
            return collect(collected)
        return receive

    return collect(())
