from time import perf_counter

from src.config import (
    ASR_BACKEND,
    FASTER_WHISPER_BEAM_SIZE,
    FASTER_WHISPER_COMPUTE_TYPE,
    FASTER_WHISPER_DEVICE,
    MODEL_REPO,
    SOURCE_LANGUAGE,
    USE_FP16,
)
from src.files import log


def _format_elapsed(seconds):
    return f"{seconds:.1f}s"


def _collect_segments_with_progress(segments, total_duration):
    segment_list = []
    next_progress_mark = 5

    for segment in segments:
        segment_list.append(
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            }
        )

        if total_duration and total_duration > 0:
            progress = min(segment.end / total_duration, 1.0)
            progress_percent = int(progress * 100)
            while progress_percent >= next_progress_mark and next_progress_mark <= 100:
                log(
                    "Transcription progress: "
                    f"{next_progress_mark}% "
                    f"({segment.end:.1f}s / {total_duration:.1f}s, "
                    f"{len(segment_list)} segments)"
                )
                next_progress_mark += 5

    if total_duration and next_progress_mark <= 100:
        log(
            "Transcription progress: "
            f"100% ({total_duration:.1f}s / {total_duration:.1f}s, "
            f"{len(segment_list)} segments)"
        )

    return segment_list


def transcribe_with_mlx(source_file):
    import mlx_whisper

    start = perf_counter()
    log(f"Initializing MLX transcription model: {MODEL_REPO}")
    log("MLX will show its own progress bar after audio preparation starts.")

    result = mlx_whisper.transcribe(
        str(source_file),
        path_or_hf_repo=MODEL_REPO,
        language=SOURCE_LANGUAGE,
        task="transcribe",
        fp16=USE_FP16,
        verbose=False,
    )
    log(f"MLX transcription finished in {_format_elapsed(perf_counter() - start)}")
    return result


def transcribe_with_faster_whisper(source_file):
    from faster_whisper import WhisperModel

    start = perf_counter()
    log(
        "Initializing faster-whisper model: "
        f"{MODEL_REPO} "
        f"(device={FASTER_WHISPER_DEVICE}, compute_type={FASTER_WHISPER_COMPUTE_TYPE})"
    )
    model = WhisperModel(
        MODEL_REPO,
        device=FASTER_WHISPER_DEVICE,
        compute_type=FASTER_WHISPER_COMPUTE_TYPE,
    )
    log(
        "Model ready in "
        f"{_format_elapsed(perf_counter() - start)} "
        f"(runtime device={model.model.device})"
    )
    decode_start = perf_counter()
    log("Preparing audio and starting transcription...")
    segments, info = model.transcribe(
        str(source_file),
        language=SOURCE_LANGUAGE,
        beam_size=FASTER_WHISPER_BEAM_SIZE,
    )
    total_duration = info.duration or 0.0
    log(
        "Transcription stream ready in "
        f"{_format_elapsed(perf_counter() - decode_start)} "
        f"(audio duration={total_duration:.1f}s, beam_size={FASTER_WHISPER_BEAM_SIZE})"
    )
    segment_list = _collect_segments_with_progress(segments, total_duration)
    log(
        "faster-whisper transcription finished in "
        f"{_format_elapsed(perf_counter() - start)}"
    )
    return {
        "segments": segment_list,
        "language": info.language,
        "language_probability": info.language_probability,
    }


def transcribe_audio(source_file):
    if ASR_BACKEND == "mlx":
        return transcribe_with_mlx(source_file)
    if ASR_BACKEND == "faster-whisper":
        return transcribe_with_faster_whisper(source_file)

    raise ValueError(
        f"Unsupported ASR_BACKEND={ASR_BACKEND!r}. Expected 'mlx' or 'faster-whisper'."
    )
