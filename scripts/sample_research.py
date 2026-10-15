"""Deprecated compatibility placeholder; no network and no market API calls.

Use the allowlisted task runner via requests/current.json.
"""
from __future__ import annotations

if __name__ == "__main__":
    print("sample_research.py is retired: it no longer calls Binance REST or emits trading signals.")
    print("Use the AISTS Research Runner workflow with an allowlisted request.")
