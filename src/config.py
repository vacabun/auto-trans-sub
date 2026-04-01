from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


# ===== 输入配置 =====
INPUT_DIR = Path("input")
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
MODEL_REPO = "mlx-community/whisper-large-v3-turbo"
SOURCE_LANGUAGE = "ja"
USE_FP16 = True

# ===== 翻译配置 =====
TARGET_LANGUAGE = "zh-Hans"
GENERATE_TRANSLATION = True
TRANSLATION_MODEL = "gpt-5.4"
TRANSLATION_BATCH_SIZE = 80

# ===== 输出配置 =====
OUTPUT_DIR = Path("output")
TRANSLATION_INDEX_FILE = OUTPUT_DIR / "translation_index.json"
SKIP_TRANSLATION_IF_EXISTS = True
