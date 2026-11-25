"""Confess Your Worst Moment — make.fun bounty entry.

Writes a single-line confession (1-200 chars, UTF-8, no trailing newline)
to $MAKEFUN_OUTPUT_DIR/entry.txt.

Usage:
    MAKEFUN_OUTPUT_DIR=/path/to/out python3 main.py

Exit codes:
    0  success
    2  MAKEFUN_OUTPUT_DIR is not set, or the entry fails validation
"""

import os
import sys

ENTRY = (
    "I tested my fix in production because staging was down, "
    "then wrote the incident report in the voice of someone "
    "who definitely tested in staging."
)


class BlankError(ValueError):
    """Raised when the entry is empty."""


class MultiLineError(ValueError):
    """Raised when the entry contains a newline or carriage return."""


class LengthError(ValueError):
    """Raised when the entry is not 1-200 characters long."""


def validate(entry: str) -> bytes:
    """Validate the entry against the contest gate and return its bytes."""
    if not entry:
        raise BlankError("entry must not be empty")
    if "\n" in entry or "\r" in entry:
        raise MultiLineError(
            "entry must be a single line (no newline characters)"
        )
    if not 1 <= len(entry) <= 200:
        raise LengthError(
            "entry must be 1-200 characters, got %d" % len(entry)
        )
    try:
        return entry.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("entry must be UTF-8 encodable: %s" % exc) from exc


def verify_written(path: str, expected: bytes) -> None:
    """Re-read the written file and raise RuntimeError if bytes differ."""
    with open(path, "rb") as fh:
        actual = fh.read()
    if actual != expected:
        raise RuntimeError(
            "read-back verification failed for %s: "
            "written bytes differ from expected (%d bytes read, "
            "%d bytes expected)" % (path, len(actual), len(expected))
        )


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print(
            "error: MAKEFUN_OUTPUT_DIR environment variable is not set",
            file=sys.stderr,
        )
        return 2

    try:
        data = validate(ENTRY)
    except (BlankError, MultiLineError, LengthError, ValueError) as exc:
        print("error: entry validation failed: %s" % exc, file=sys.stderr)
        return 2

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "wb") as fh:
        fh.write(data)

    try:
        verify_written(out_path, data)
    except RuntimeError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
