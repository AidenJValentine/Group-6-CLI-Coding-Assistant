"""
setup_calculator_app.py
=======================
Run this script once to create the calculator_app/ folder and populate it
with calculator.py and README.md.

Usage:
    python setup_calculator_app.py
"""

import os

# ---------------------------------------------------------------------------
# File contents
# ---------------------------------------------------------------------------

CALCULATOR_PY = '''"""
calculator.py
=============
A simple calculator module implementing add, subtract, multiply, and divide
operations with robust error handling following Python best practices.

Best practices applied:
- Catch specific exceptions (ValueError, TypeError, ZeroDivisionError)
- Use custom exceptions for domain-specific errors
- Provide clear, informative error messages
- Validate inputs before processing
- Separate concerns: pure functions + an interactive loop
"""


# ---------------------------------------------------------------------------
# Custom Exception
# ---------------------------------------------------------------------------

class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""
    pass


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------

def add(a: float, b: float) -> float:
    """Return the sum of a and b.

    Args:
        a: First operand.
        b: Second operand.

    Returns:
        The result of a + b.

    Raises:
        TypeError: If either argument is not a number.
    """
    _validate_numbers(a, b)
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of a and b.

    Args:
        a: First operand.
        b: Second operand.

    Returns:
        The result of a - b.

    Raises:
        TypeError: If either argument is not a number.
    """
    _validate_numbers(a, b)
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of a and b.

    Args:
        a: First operand.
        b: Second operand.

    Returns:
        The result of a * b.

    Raises:
        TypeError: If either argument is not a number.
    """
    _validate_numbers(a, b)
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of a divided by b.

    Args:
        a: Numerator.
        b: Denominator.

    Returns:
        The result of a / b.

    Raises:
        TypeError: If either argument is not a number.
        ZeroDivisionError: If b is zero.
    """
    _validate_numbers(a, b)
    if b == 0:
        raise ZeroDivisionError(
            "Division by zero is not allowed. Please provide a non-zero denominator."
        )
    return a / b


# ---------------------------------------------------------------------------
# Input Validation Helper
# ---------------------------------------------------------------------------

def _validate_numbers(*args) -> None:
    """Ensure all arguments are integers or floats.

    Raises:
        TypeError: If any argument is not a numeric type.
    """
    for value in args:
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Expected a numeric value, but got \'{type(value).__name__}\': {value!r}. "
                "Please provide integers or floats only."
            )


# ---------------------------------------------------------------------------
# Safe Input Helper (used by the interactive loop)
# ---------------------------------------------------------------------------

def _get_number(prompt: str) -> float:
    """Repeatedly prompt the user until a valid float is entered.

    Args:
        prompt: The message displayed to the user.

    Returns:
        A validated float entered by the user.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  ✗ Invalid input — please enter a numeric value (e.g. 3, -1.5, 0.75).\\n")


# ---------------------------------------------------------------------------
# Operation Dispatcher
# ---------------------------------------------------------------------------

OPERATIONS = {
    "add":      (add,      "+"),
    "subtract": (subtract, "-"),
    "multiply": (multiply, "*"),
    "divide":   (divide,   "/"),
}


def calculate(operation: str, a: float, b: float) -> float:
    """Dispatch to the correct operation function.

    Args:
        operation: One of \'add\', \'subtract\', \'multiply\', \'divide\'.
        a: First operand.
        b: Second operand.

    Returns:
        Result of the chosen operation.

    Raises:
        CalculatorError: If the operation name is not recognised.
        TypeError: Propagated from the operation if inputs are invalid.
        ZeroDivisionError: Propagated from divide() when b == 0.
    """
    if operation not in OPERATIONS:
        valid = ", ".join(OPERATIONS.keys())
        raise CalculatorError(
            f"Unknown operation \'{operation}\'. Valid operations are: {valid}."
        )
    func, _ = OPERATIONS[operation]
    return func(a, b)


# ---------------------------------------------------------------------------
# Interactive Calculator Loop
# ---------------------------------------------------------------------------

def run_calculator() -> None:
    """Launch an interactive command-line calculator session."""
    print("=" * 45)
    print("        Welcome to the Python Calculator")
    print("=" * 45)
    print("Available operations: add, subtract, multiply, divide")
    print("Type \'exit\' at the operation prompt to quit.\\n")

    last_result = None   # Allows chaining results between operations

    while True:
        try:
            # ---- First number (or reuse last result) ----
            if last_result is not None:
                reuse = input(
                    f"  Reuse last result ({last_result}) as first number? [y/n]: "
                ).strip().lower()
                if reuse == "y":
                    a = last_result
                    print(f"  Using {a} as the first number.")
                else:
                    a = _get_number("  Enter first number : ")
            else:
                a = _get_number("  Enter first number : ")

            # ---- Operation ----
            operation = input("  Enter operation    : ").strip().lower()
            if operation == "exit":
                print("\\n  Goodbye! Thanks for using the calculator. 👋")
                break

            # ---- Second number ----
            b = _get_number("  Enter second number: ")

            # ---- Calculate ----
            result = calculate(operation, a, b)

            # ---- Display result ----
            _, symbol = OPERATIONS[operation]
            print(f"\\n  ✔  {a} {symbol} {b} = {result}\\n")
            last_result = result

        except ZeroDivisionError as e:
            print(f"\\n  ✗ Math Error     : {e}\\n")
            last_result = None

        except CalculatorError as e:
            print(f"\\n  ✗ Operation Error: {e}\\n")

        except TypeError as e:
            print(f"\\n  ✗ Type Error     : {e}\\n")

        except KeyboardInterrupt:
            print("\\n\\n  Interrupted. Goodbye! 👋")
            break


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_calculator()
'''

README_MD = """# Calculator App

A clean Python command-line calculator with robust error handling.

## Features
- **Four operations**: add, subtract, multiply, divide
- **Custom exception** (`CalculatorError`) for unknown operations
- **Type validation** — rejects non-numeric inputs with clear messages
- **Division-by-zero guard** — raises `ZeroDivisionError` with a friendly message
- **Result chaining** — reuse the previous result as the first operand
- **Graceful exit** — handles `KeyboardInterrupt` (Ctrl+C) cleanly

## Usage
```bash
python calculator.py
```

## Example Session
```
=============================================
        Welcome to the Python Calculator
=============================================
Available operations: add, subtract, multiply, divide
Type 'exit' at the operation prompt to quit.

  Enter first number : 10
  Enter operation    : divide
  Enter second number: 0

  ✗ Math Error     : Division by zero is not allowed. Please provide a non-zero denominator.

  Enter first number : 10
  Enter operation    : divide
  Enter second number: 4

  ✔  10.0 / 4.0 = 2.5
```

## Error Handling Summary
| Error Type          | Trigger                              | Response                        |
|---------------------|--------------------------------------|---------------------------------|
| `ValueError`        | Non-numeric input at the prompt      | Re-prompts with helpful message |
| `ZeroDivisionError` | Dividing by zero                     | Prints error, resets state      |
| `TypeError`         | Non-numeric args passed to functions | Prints type error message       |
| `CalculatorError`   | Unknown operation string             | Lists valid operations          |
| `KeyboardInterrupt` | Ctrl+C                               | Exits gracefully                |
"""

# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

FOLDER = "calculator_app"

def main():
    # Create folder
    os.makedirs(FOLDER, exist_ok=True)
    print(f"✔  Created folder: {FOLDER}/")

    # Write calculator.py
    calc_path = os.path.join(FOLDER, "calculator.py")
    with open(calc_path, "w", encoding="utf-8") as f:
        f.write(CALCULATOR_PY)
    print(f"✔  Written file  : {calc_path}")

    # Write README.md
    readme_path = os.path.join(FOLDER, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(README_MD)
    print(f"✔  Written file  : {readme_path}")

    print("\nAll done! Run your calculator with:")
    print(f"    python {FOLDER}/calculator.py")


if __name__ == "__main__":
    main()
