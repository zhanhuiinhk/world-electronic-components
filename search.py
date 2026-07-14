#!/usr/bin/env python3
"""Backward-compatible entrypoint. Prefer: python scripts/search.py <keyword>"""

from scripts.search import main

if __name__ == "__main__":
    main()
