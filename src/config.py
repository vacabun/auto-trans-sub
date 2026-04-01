import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


# ===== 输入配置 =====
INPUT_DIR = Path(os.getenv("INPUT_DIR", "input"))
SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".mp4",
    ".mkv",
    ".mov",
    ".flac",
    ".aac",
    ".ogg",
    ".webm",
}

# ===== 识别配置 =====
MODEL_REPO = os.getenv("WHISPER_MODEL_REPO", "mlx-community/whisper-large-v3-mlx")
SOURCE_LANGUAGE = os.getenv("SOURCE_LANGUAGE", "ja")
USE_FP16 = os.getenv("USE_FP16", "true").lower() in {"1", "true", "yes", "on"}

# ===== 翻译配置 =====
TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", "zh-Hans")
GENERATE_TRANSLATION = os.getenv("GENERATE_TRANSLATION", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "gpt-5.4")
TRANSLATION_BATCH_SIZE = int(os.getenv("TRANSLATION_BATCH_SIZE", "80"))

# ===== 输出配置 =====
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
TRANSLATION_INDEX_FILE = OUTPUT_DIR / "translation_index.json"
SKIP_TRANSLATION_IF_EXISTS = os.getenv(
    "SKIP_TRANSLATION_IF_EXISTS", "true"
).lower() in {"1", "true", "yes", "on"}
