from datetime import datetime

from src.config import (
    GENERATE_TRANSLATION,
    MODEL_REPO,
    SKIP_TRANSLATION_IF_EXISTS,
    TARGET_LANGUAGE,
    TRANSLATION_INDEX_FILE,
    TRANSLATION_MODEL,
)
from src.files import (
    build_output_paths,
    ensure_output_dir,
    list_input_files,
    log,
    read_json,
    write_json,
)
from src.subtitles import load_segments, parse_srt, save_segments, write_srt
from src.transcription import transcribe_audio
from src.translation import translate_segments_with_ai


def load_translation_index():
    return read_json(TRANSLATION_INDEX_FILE, default={})


def update_translation_index(source_file, paths, translated):
    index = load_translation_index()
    source_key = str(source_file)
    index[source_key] = {
        "source_file": source_key,
        "japanese_subtitle_file": str(paths["ja_srt"]),
        "japanese_segments_file": str(paths["segments_json"]),
        "translated_subtitle_file": str(paths["translation_srt"]) if translated else "",
        "bilingual_subtitle_file": str(paths["bilingual_srt"]) if translated else "",
        "translated": translated,
        "translation_model": TRANSLATION_MODEL if translated else "",
        "target_language": TARGET_LANGUAGE if translated else "",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    write_json(TRANSLATION_INDEX_FILE, index)


def load_existing_japanese_segments(paths):
    if paths["segments_json"].exists():
        segments = load_segments(paths["segments_json"])
        if segments:
            log(f"Reusing Japanese segments: {paths['segments_json']}")
            return segments

    if paths["ja_srt"].exists():
        segments = parse_srt(paths["ja_srt"])
        if segments:
            log(f"Reusing Japanese subtitles: {paths['ja_srt']}")
            save_segments(paths["segments_json"], segments)
            return segments

    return None


def should_skip_translation(paths):
    return (
        SKIP_TRANSLATION_IF_EXISTS
        and paths["translation_srt"].exists()
        and paths["bilingual_srt"].exists()
    )


def process_file(source_file, file_no, file_total):
    log(f"[{file_no}/{file_total}] Processing: {source_file}")
    paths = build_output_paths(source_file, TARGET_LANGUAGE)

    segments_ja = load_existing_japanese_segments(paths)
    if segments_ja is None:
        log(f"Loading MLX Whisper model: {MODEL_REPO}")
        log("Starting Japanese transcription...")
        result_ja = transcribe_audio(source_file)
        segments_ja = result_ja["segments"]
        log(f"Transcription complete: {len(segments_ja)} segments")

        write_srt(paths["ja_srt"], segments_ja)
        save_segments(paths["segments_json"], segments_ja)
        log(f"Generated: {paths['ja_srt']}")
        log(f"Generated: {paths['segments_json']}")
    else:
        write_srt(paths["ja_srt"], segments_ja)
        log(f"Japanese subtitles ready: {paths['ja_srt']}")

    if not GENERATE_TRANSLATION:
        update_translation_index(source_file, paths, translated=False)
        return

    if should_skip_translation(paths):
        log(f"Translation already exists, skipping: {paths['translation_srt']}")
        update_translation_index(source_file, paths, translated=True)
        return

    log(f"Starting AI translation to {TARGET_LANGUAGE}...")
    segments_translation = translate_segments_with_ai(segments_ja)

    write_srt(paths["translation_srt"], segments_translation)
    write_srt(paths["bilingual_srt"], segments_ja, segments_translation)
    log(f"Generated: {paths['translation_srt']}")
    log(f"Generated: {paths['bilingual_srt']}")

    update_translation_index(source_file, paths, translated=True)


def main():
    ensure_output_dir()
    input_files = list_input_files()
    if not input_files:
        log("No supported media files found under input/.")
        return

    failures = []
    total = len(input_files)
    log(f"Found {total} input files under input/.")

    for file_no, source_file in enumerate(input_files, start=1):
        try:
            process_file(source_file, file_no, total)
        except Exception as exc:
            failures.append((source_file, str(exc)))
            log(f"Failed: {source_file}")
            log(str(exc))

    if failures:
        failed_files = ", ".join(str(path) for path, _ in failures)
        raise RuntimeError(f"Completed with {len(failures)} failures: {failed_files}")
