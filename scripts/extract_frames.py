#!/usr/bin/env python3
"""Extract one high-quality JPG every N seconds from each labeling clip."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def extract_clip(src: Path, dest_dir: Path, every_seconds: float) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    pattern = dest_dir / f"{src.stem}_%04d.jpg"
    for old in dest_dir.glob(f"{src.stem}_*.jpg"):
        old.unlink()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            f"fps=1/{every_seconds}",
            "-q:v",
            "2",
            str(pattern),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return len(list(dest_dir.glob(f"{src.stem}_*.jpg")))


def member_clips(root: Path) -> list[tuple[str, Path]]:
    clips = []
    for path in sorted(root.glob("*/*.mp4")):
        if not path.is_file():
            continue
        if path.parent.name == "frames" or path.parent.name.startswith("frames_"):
            continue
        clips.append((path.parent.name, path))
    return clips


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract one JPG every N seconds from each member clip."
    )
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--every-seconds", type=float, default=2.0)
    args = parser.parse_args()

    if args.every_seconds <= 0:
        raise SystemExit("--every-seconds must be > 0")
    if not args.input_dir.is_dir():
        raise SystemExit(f"Input dir not found: {args.input_dir}")

    clips = member_clips(args.input_dir)
    if not clips:
        raise SystemExit(f"No mp4 files in {args.input_dir}/*/")

    totals: dict[str, int] = {}
    for member, src in clips:
        dest = args.input_dir / f"frames_{member}"
        count = extract_clip(src, dest, args.every_seconds)
        totals[member] = totals.get(member, 0) + count
        print(f"{member}: {src.name} -> {count} frames")

    print("----")
    for member, count in totals.items():
        print(f"{member}: {count} frames")
    print(f"total: {sum(totals.values())} frames")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
