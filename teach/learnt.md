# Learning log

Concepts covered while reading through `src/pisa_py/io.py`.

## `pathlib.Path`
- Object-oriented filesystem paths; `Path(...)` doesn't touch disk on its own.
- `/` joins path segments (`Path.__truediv__`, operator overloading — not division).
- `Path(__file__)` is the path to the current module's own file.
- `.parent` / `.parents[n]` walk up the directory tree; `.parents[0] == .parent`.
- `.resolve()` makes a path absolute.
- `.exists()`, `.mkdir(parents=True, exist_ok=True)` for filesystem checks/setup.

## Strings and comments
- `"""..."""` is a real string literal, not a comment. In docstring position
  (first statement of a module/function/class) it becomes `.__doc__`.
- `#` is a true comment, discarded by the parser, never exists at runtime.
- `.strip()` removes whitespace from both ends; `.lstrip(char)` removes a
  specific character from the left only (e.g. a UTF-8 BOM, `"﻿"`).

## `dict` and unpacking
- `dict.fromkeys(iterable)` builds a dict with each element as a key
  (value `None`) — dedupes because dict keys are unique, and preserves
  insertion order (Python 3.7+).
- `*x` inside a list literal (`[*x, *y]`) unpacks/spreads `x`'s elements in
  place, rather than nesting `x` as a single item — same idea as JS `...`.
- Pattern used repeatedly in this file: `list(dict.fromkeys([*a, *b, ...]))`
  = concatenate several lists, then dedupe while keeping order.

## List comprehensions
- Shape: `[<expression> for <item> in <iterable> if <condition>]`.
- The leading expression and the loop variable are separate things — the
  expression can be anything, not just the bare loop variable.

## The walrus operator `:=`
- Assigns and evaluates to that value in one expression, e.g.
  `if missing := [...]:` assigns `missing` and uses it as the condition,
  so it's still available inside the `if` block. Python 3.8+.

## Conditional (ternary) expression
- `value_if_true if condition else value_if_false` — an expression, not a
  statement. Equivalent in spirit to JS's `condition ? a : b`, reordered
  to read like a sentence.

## Exceptions
- `raise SomeError(...)` immediately aborts normal execution and propagates
  up the call stack — not a console print, a real interruption (unless
  caught by `try`/`except`).
- `KeyError` conventionally means "lookup not found"; reused here for
  "requested column missing" even without a literal dict lookup.

## Polars-specific
- Expressions (`pl.col(...)`) are lazy — they describe a plan, and only run
  when passed to something that executes it (e.g. `.filter()`, `.collect()`).
- Namespace accessors like `.str` (also `.dt`, `.list`) group type-specific
  operations on an expression/column — not a type cast.
- `.filter(...)` uses a boolean mask (one bool per row) to select rows;
  the mask isn't stored as a column.
- `pl.scan_parquet(...)` returns a `LazyFrame` — a plan over the file,
  not loaded data. Lets column selection get pushed down to the reader.
- `.sink_parquet(...)` executes a lazy plan and streams the result straight
  to disk, without materializing the full result in memory first.
- Row counts aren't free metadata like column names are — getting them
  (`.select(pl.len()).collect().item()`) is a real, if cheap, computation.

## `set`
- `set` as a noun: an unordered, duplicate-free collection type, built for
  fast (~O(1)) membership testing (`x in a_set`), unlike `list` (O(n)).

## `zip`
- Pairs up multiple iterables element-by-element into tuples; lazy, usually
  wrapped in `list(...)` or fed into `dict(...)`.
- `strict=True` (3.10+) raises if the iterables have mismatched lengths,
  instead of silently truncating.

## Method chaining
- `.method().method()` reads similarly to R's `|>`/`%>%` pipelines, but the
  mechanism differs — each `.method()` is a call defined on that object's
  class, not syntactic rewriting.
