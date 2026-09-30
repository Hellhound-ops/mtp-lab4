"""Проверка функциональных решений, ленивости и независимости потоков."""

from itertools import islice
import os
from pathlib import Path
import random
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from functional import curry, total
from generators import fibonacci, random_data, random_numbers


class ReduceTests(unittest.TestCase):
    def test_values_and_empty(self):
        self.assertEqual(total([7, -2, 10, 5]), 20)
        self.assertEqual(total([]), 0)
        self.assertEqual(total([-4]), -4)

    def test_single_pass_iterable(self):
        source = iter([2, 4, 6])
        self.assertEqual(total(source), 12)
        self.assertEqual(list(source), [])

    def test_does_not_modify_list(self):
        source = [3, -5, 8]
        total(source)
        self.assertEqual(source, [3, -5, 8])

    def test_invalid_items(self):
        for item in (True, 1.5, "3"):
            with self.assertRaises(TypeError):
                total([item])


class FibonacciTests(unittest.TestCase):
    def test_first_ten(self):
        self.assertEqual(list(islice(fibonacci(), 10)),
                         [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

    def test_pause_and_resume(self):
        stream = fibonacci()
        self.assertEqual(list(islice(stream, 0)), [])
        self.assertEqual(next(stream), 0)
        self.assertEqual(list(islice(stream, 4)), [1, 1, 2, 3])
        self.assertEqual(next(stream), 5)

    def test_recurrence(self):
        values = list(islice(fibonacci(), 100))
        for i in range(2, 100):
            self.assertEqual(values[i], values[i - 1] + values[i - 2])


class RandomTests(unittest.TestCase):
    def test_count_bounds_and_repeatability(self):
        values = list(random_numbers(-3, 4, 100, seed=11))
        self.assertEqual(len(values), 100)
        self.assertTrue(all(-3 <= value <= 4 for value in values))
        self.assertEqual(values, list(random_numbers(-3, 4, 100, seed=11)))
        reference = random.Random(11)
        expected = [reference.randint(-3, 4) for _ in range(100)]
        self.assertEqual(values, expected)

    def test_equal_bounds_and_zero_count(self):
        self.assertEqual(list(random_numbers(7, 7, 3)), [7, 7, 7])
        self.assertEqual(list(random_numbers(1, 5, 0)), [])

    def test_invalid_arguments(self):
        for args in ((5, 1, 3), (1, 5, -1)):
            with self.assertRaises(ValueError):
                next(random_numbers(*args))
        with self.assertRaises(TypeError):
            next(random_numbers(1, 5, True))
        with self.assertRaises(TypeError):
            next(random_numbers(1.5, 5, 3))

    def test_global_state_unchanged(self):
        before = random.getstate()
        list(random_numbers(1, 9, 20, seed=7))
        list(islice(random_data(seed=9), 10))
        self.assertEqual(before, random.getstate())

    def test_independent_streams(self):
        left = random_numbers(1, 100, 8, seed=17)
        right = random_numbers(1, 100, 8, seed=17)
        self.assertEqual([next(left) for _ in range(3)],
                         [next(right) for _ in range(3)])
        self.assertEqual(list(left), list(right))

    def test_endless_data_resume(self):
        stream = random_data(10, 12, seed=6)
        records = list(islice(stream, 1000))
        self.assertEqual([row["number"] for row in records],
                         list(range(1, 1001)))
        self.assertTrue(all(10 <= row["value"] <= 12 for row in records))
        self.assertEqual(next(stream)["number"], 1001)

    def test_records_are_independent(self):
        stream = random_data(2, 2)
        first = next(stream)
        first["value"] = 999
        self.assertEqual(next(stream), {"number": 2, "value": 2})

    def test_data_validation(self):
        with self.assertRaises(ValueError):
            next(random_data(9, 1))
        with self.assertRaises(TypeError):
            next(random_data(True, 5))


class CurryTests(unittest.TestCase):
    def test_three_and_one_argument(self):
        self.assertEqual(curry(lambda a, b, c: a * b + c)(3)(4)(2), 14)
        self.assertEqual(curry(lambda x: x * x)(5), 25)

    def test_no_early_evaluation_and_branching(self):
        calls = []

        def expression(a, b, c):
            calls.append((a, b, c))
            return a + b + c

        first = curry(expression)(10)
        second = first(20)
        self.assertEqual(calls, [])
        self.assertEqual(second(1), 31)
        self.assertEqual(second(2), 32)
        self.assertEqual(first(30)(3), 43)
        self.assertEqual(len(calls), 3)

    def test_positional_only(self):
        def subtract(a, b, /):
            return a - b
        self.assertEqual(curry(subtract)(8)(3), 5)

    def test_unsupported_signatures(self):
        functions = [lambda: 1, lambda x=1: x, lambda *args: args,
                     lambda **kwargs: kwargs, lambda *, x: x]
        for function in functions:
            with self.assertRaises(ValueError):
                curry(function)
        with self.assertRaises(TypeError):
            curry(42)

    def test_only_one_argument_per_call(self):
        curried = curry(lambda a, b: a + b)
        with self.assertRaises(TypeError):
            curried(1, 2)

    def test_original_error_propagates(self):
        with self.assertRaises(ZeroDivisionError):
            curry(lambda a, b: a / b)(3)(0)


class CommandTests(unittest.TestCase):
    def run_command(self, *arguments):
        main = Path(__file__).resolve().parent / "main.py"
        with TemporaryDirectory() as folder:
            return subprocess.run(
                [sys.executable, str(main), *arguments], cwd=folder,
                capture_output=True, text=True, encoding="utf-8", timeout=10,
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )

    def test_full_demo_finishes(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("Сумма через reduce: 20", "3 * 4 + 2 = 14",
                     "'number': 8", "Среднее №5"):
            self.assertIn(text, result.stdout)

    def test_custom_input(self):
        result = self.run_command("--task", "sum", "--numbers", "-5", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reduce: -3", result.stdout)
        zero = self.run_command("--count", "0")
        self.assertEqual(zero.returncode, 0, zero.stderr)
        self.assertNotIn("'number':", zero.stdout)

    def test_invalid_input(self):
        for args in (("--count", "-1"), ("--low", "9", "--high", "2"),
                     ("--numbers", "abc")):
            result = self.run_command(*args)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
