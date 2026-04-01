import json
import re
from pathlib import Path

from src.config import INPUT_DIR, OUTPUT_DIR, SUPPORTED_EXTENSIONS


def log(message):
    print(message, flush=True)


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path, default=None):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def slugify_filename(name):
    return re.sub(r"[^\w\-.]+", "_", name).strip("_") or "subtitle"


def relative_input_stem(source_file):
    relative_path = source_file.relative_to(INPUT_DIR)
    return relative_path.with_suffix("").as_posix()


def build_output_paths(source_file, target_language):
    stem = slugify_filename(relative_input_stem(source_file))
    return {
        "ja_srt": OUTPUT_DIR / f"{stem}.ja.srt",
        "translation_srt": OUTPUT_DIR / f"{stem}.{target_language}.srt",
        "bilingual_srt": OUTPUT_DIR / f"{stem}.bilingual.srt",
        "segments_json": OUTPUT_DIR / f"{stem}.ja.segments.json",
    }


def list_input_files():
    if not INPUT_DIR.exists():
        return []

    files = [
        path
        for path in INPUT_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files)
