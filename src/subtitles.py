import re
from datetime import timedelta

from src.files import read_json, write_json


def format_time(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int(round((seconds - total_seconds) * 1000))
    if ms == 1000:
        total_seconds += 1
        ms = 0
    return str(timedelta(seconds=total_seconds)) + f",{ms:03d}"


def parse_timecode(value):
    hours, minutes, seconds_ms = value.split(":")
    seconds, ms = seconds_ms.split(",")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(ms) / 1000
    )


def write_srt(filename, primary_segments, secondary_segments=None):
    with open(filename, "w", encoding="utf-8") as f:
        for i, segment in enumerate(primary_segments, start=1):
            start = format_time(segment["start"])
            end = format_time(segment["end"])
            primary_text = segment["text"].strip()

            if secondary_segments:
                secondary_text = secondary_segments[i - 1]["text"].strip()
                text = f"{primary_text}\n{secondary_text}" if secondary_text else primary_text
            else:
                text = primary_text

            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


def parse_srt(path):
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    segments = []
    for block in re.split(r"\n\s*\n", content):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        timeline = lines[1]
        start_str, end_str = timeline.split(" --> ")
        text = "\n".join(lines[2:]).strip()
        segments.append(
            {
                "start": parse_timecode(start_str),
                "end": parse_timecode(end_str),
                "text": text,
            }
        )
    return segments


def save_segments(path, segments):
    write_json(path, {"segments": segments})


def load_segments(path):
    data = read_json(path, default={})
    return data.get("segments", [])
