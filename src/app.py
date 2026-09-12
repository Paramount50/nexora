"""Compatibility entry point for the unified Nexora web application.

The production UI is the React build served by ``backend.main``.  This module
keeps the old import path usable without bringing back a second UI runtime.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
