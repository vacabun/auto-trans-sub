import mlx_whisper

from src.config import MODEL_REPO, SOURCE_LANGUAGE, USE_FP16


def transcribe_audio(source_file):
    return mlx_whisper.transcribe(
        str(source_file),
        path_or_hf_repo=MODEL_REPO,
        language=SOURCE_LANGUAGE,
        task="transcribe",
        fp16=USE_FP16,
        verbose=False,
    )
