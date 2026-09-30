"""Демонстрация пяти заданий функционального программирования."""

import argparse
from itertools import islice

from functional import curry, total
from generators import fibonacci, random_data, random_numbers


def weighted_sum(a: int, b: int, c: int) -> int:
    """Функция трёх аргументов для примера каррирования: a * b + c."""
    return a * b + c


def main() -> None:
    parser = argparse.ArgumentParser(description="ЛР №4, вариант 3")
    parser.add_argument(
        "--task", choices=["all", "sum", "fibonacci", "random", "curry", "stream"],
        default="all",
    )
    parser.add_argument("--numbers", type=int, nargs="*", default=[7, -2, 10, 5])
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--low", type=int, default=1)
    parser.add_argument("--high", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--a", type=int, default=3)
    parser.add_argument("--b", type=int, default=4)
    parser.add_argument("--c", type=int, default=2)
    args = parser.parse_args()
    if args.count < 0:
        parser.error("Количество не может быть отрицательным")
    if args.task in ("all", "random", "stream") and args.low > args.high:
        parser.error("Нижняя граница больше верхней")

    print("Бодров Георгий Александрович, группа 221341, вариант 3, ЛР №4")
    if args.task in ("all", "sum"):
        print("Среднее №3. Сумма через reduce:", total(args.numbers))
    if args.task in ("all", "fibonacci"):
        print("Среднее №5. Генератор Фибоначчи:")
        print(list(islice(fibonacci(), args.count)))
    if args.task in ("all", "random"):
        print("Среднее №9. Случайные числа в диапазоне:")
        print(list(random_numbers(args.low, args.high, args.count,
                                  seed=args.seed)))
    if args.task in ("all", "curry"):
        curried = curry(weighted_sum)
        with_a = curried(args.a)
        with_a_b = with_a(args.b)
        print("Повышенное №3. Каррирование:")
        print(f"{args.a} * {args.b} + {args.c} = {with_a_b(args.c)}")
        print("Прямой вызов:", weighted_sum(args.a, args.b, args.c))
    if args.task in ("all", "stream"):
        print("Повышенное №7. Первые записи бесконечного генератора:")
        stream = random_data(args.low, args.high, seed=args.seed)
        for record in islice(stream, args.count):
            print(record)


if __name__ == "__main__":
    main()
