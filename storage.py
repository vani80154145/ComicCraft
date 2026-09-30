from pathlib import Path
import re
from uuid import uuid4


def safe_filename(
    value: str,
    suffix: str = ".png"
) -> str:

    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value
    )

    cleaned = cleaned.strip("_")

    if not cleaned:
        cleaned = "panel"

    cleaned = cleaned[:60]

    return (
        f"{cleaned}_"
        f"{uuid4().hex[:8]}"
        f"{suffix}"
    )


def relative_static_url(
    path: Path,
    static_dir: Path
) -> str:

    return "/" + path.relative_to(
        static_dir.parent
    ).as_posix()