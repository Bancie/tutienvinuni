#!/usr/bin/env python3
"""Split each video into equal contiguous parts and assign part k to member k."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def split_video(src: Path, work_dir: Path, members: int) -> list[Path]:
    duration = probe_duration(src)
    if duration <= 0:
        raise SystemExit(f"{src.name} has no duration")
    times = ",".join(f"{duration * i / members:.3f}" for i in range(1, members))
    work_dir.mkdir(parents=True, exist_ok=True)
    for old in work_dir.glob("part*.mp4"):
        old.unlink()
    pattern = str(work_dir / "part%02d.mp4")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-map",
            "0",
            "-c",
            "copy",
            "-f",
            "segment",
            "-segment_times",
            times,
            "-reset_timestamps",
            "1",
            "-segment_start_number",
            "1",
            pattern,
        ],
        check=True,
    )
    parts = [work_dir / f"part{i:02d}.mp4" for i in range(1, members + 1)]
    missing = [p.name for p in parts if not p.is_file() or p.stat().st_size == 0]
    extra = sorted(p.name for p in work_dir.glob("part*.mp4") if p not in parts)
    if missing or extra:
        raise SystemExit(
            f"{src.name}: expected {members} parts, missing={missing or '-'} extra={extra or '-'}"
        )
    return parts


def source_videos(input_dir: Path, output_dir: Path) -> list[Path]:
    videos = sorted(p for p in input_dir.glob("*.mp4") if p.is_file())
    output_resolved = output_dir.resolve()
    kept = []
    for video in videos:
        if output_resolved in video.resolve().parents:
            continue
        kept.append(video)
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split each mp4 into N contiguous parts, one part per member."
    )
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--names",
        default="nam,tuan,dat,bang,nghia",
        help="Comma-separated folder names, in part order. Part 1 goes to the first name.",
    )
    parser.add_argument(
        "--members",
        type=int,
        default=None,
        help="Number of parts. Defaults to the number of --names.",
    )
    args = parser.parse_args()

    names = [name.strip() for name in args.names.split(",") if name.strip()]
    if not names:
        raise SystemExit("--names must include at least one name")
    if args.members is None:
        args.members = len(names)
    if args.members < 1:
        raise SystemExit("--members must be >= 1")
    if len(names) != args.members:
        raise SystemExit(
            f"--names has {len(names)} entries but --members is {args.members}"
        )
    if not args.input_dir.is_dir():
        raise SystemExit(f"Input dir not found: {args.input_dir}")

    videos = source_videos(args.input_dir, args.output_dir)
    if not videos:
        raise SystemExit(f"No mp4 files in {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    member_dirs = []
    for name in names:
        member_dir = args.output_dir / name
        member_dir.mkdir(parents=True, exist_ok=True)
        member_dirs.append(member_dir)

    rows = ["member\tsource\tstart_sec\tend_sec\toutput"]
    for src in videos:
        print(f"Splitting {src.name} ({probe_duration(src):.3f}s) into {args.members} parts")
        work = args.output_dir / "_tmp" / src.stem
        parts = split_video(src, work, args.members)
        cursor = 0.0
        for index, part in enumerate(parts, start=1):
            duration = probe_duration(part)
            dest = member_dirs[index - 1] / f"{src.stem}_part{index}of{args.members}.mp4"
            if dest.exists():
                dest.unlink()
            part.replace(dest)
            end = cursor + duration
            member_name = names[index - 1]
            rows.append(
                f"{member_name}\t{src.name}\t{cursor:.3f}\t{end:.3f}\t{dest.relative_to(args.output_dir)}"
            )
            print(f"  {member_name}: {dest.name} {duration:.3f}s ({cursor:.3f}-{end:.3f})")
            cursor = end
        work.rmdir()

    tmp_root = args.output_dir / "_tmp"
    if tmp_root.is_dir():
        try:
            tmp_root.rmdir()
        except OSError:
            pass

    manifest = args.output_dir / "manifest.tsv"
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {manifest}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
