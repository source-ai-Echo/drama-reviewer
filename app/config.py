from __future__ import annotations

import os
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parent


def load_local_env() -> None:
    """Load simple KEY=VALUE entries without logging secret values."""
    candidates = (APP_ROOT / ".env.local", WORKSPACE_ROOT / ".env.local")
    for path in candidates:
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                os.environ.setdefault(key, value)


load_local_env()

CORPUS_ROOT = Path(
    os.getenv("DRAMA_CORPUS_ROOT", str(APP_ROOT / "sample-corpus"))
).resolve()
PUBLIC_SKILL_ROOT = Path(
    os.getenv("DRAMA_SKILL_ROOT", str(WORKSPACE_ROOT))
).resolve()
