"""
Helper script to generate a bcrypt hash for Streamlit secrets.

Usage:
  python generate_hash.py

Then copy the printed string into `.streamlit/secrets.toml` as:
  PASSWORD_HASH = "<printed_hash>"
"""

from __future__ import annotations

import getpass

import bcrypt


def main() -> None:
    password = getpass.getpass("Password to hash: ")
    if not password:
        raise SystemExit("Password cannot be empty.")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    print(hashed.decode("utf-8"))


if __name__ == "__main__":
    main()

