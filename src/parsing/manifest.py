"""Build a conservative manifest for mixed-format resume files."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xml"}


def build_manifest(root: Path, project_root: Path | None = None) -> dict[str, Any]:
    project_root = project_root or root
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for path in sorted(root.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        group_key = normalize_stem(path.stem)
        grouped[group_key].append(
            {
                "path": path.relative_to(project_root).as_posix(),
                "filename": path.name,
                "format": path.suffix.lower().lstrip("."),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    groups = [
        {
            "candidate_key": key,
            "files": files,
            "formats": sorted({item["format"] for item in files}),
            "needs_review": len(files) > 1,
        }
        for key, files in sorted(grouped.items())
    ]
    return {
        "source_directory": root.relative_to(project_root).as_posix(),
        "file_count": sum(len(group["files"]) for group in groups),
        "group_count": len(groups),
        "variant_group_count": sum(group["needs_review"] for group in groups),
        "groups": groups,
    }


def normalize_stem(stem: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    source = project_root / "data" / "dummy_resumes" / "Dummy Resumes"
    output = project_root / "data" / "dummy_manifest.json"
    manifest = build_manifest(source, project_root)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        f"Manifested {manifest['file_count']} files into "
        f"{manifest['group_count']} groups; {manifest['variant_group_count']} need review"
    )
