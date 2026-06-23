from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from pathlib import Path

from .schema import Candidate


def stream_candidates(path: str | Path, limit: int | None = None) -> Iterator[Candidate]:
    path = Path(path)
    bad = n = 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            yield Candidate.from_raw(obj)
            n += 1
            if limit is not None and n >= limit:
                break
    if bad:
        print(f"[trustrank.io] skipped {bad} malformed line(s)", file=sys.stderr)
