# Order calculator

A small Python project that calculates an order total from decimal prices and quantities.

## Setup

Requires Python 3.10 or newer. No additional packages are needed.

## Run

From this repository's root folder:

```sh
python demo.py
python -m unittest discover -s tests -v
```

Use `python3` if that is the Python command on your machine.

## Files

- `src/order_total/pricing.py`: the calculator.
- `demo.py`: an example caller.
- `tests/test_pricing.py`: automated checks.
