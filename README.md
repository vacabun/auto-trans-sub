# auto-trans-sub

使用 `mlx-whisper` 在 Apple Silicon Mac 上批量处理 `input/` 里的音视频文件，先做日语语音识别，再直接用 LLM 把识别出的文本分段翻译成中文，不再进行第二遍语音识别。

## 安装

先安装 `ffmpeg`：

```bash
brew install ffmpeg
```

再安装 Python 依赖：

```bash
pip install -r requirements.txt
```

复制一份本地配置：

```bash
cp .env.example .env
```

然后编辑 `.env`，填入你的 key：

```env
OPENAI_API_KEY=your_api_key
```

默认使用 OpenAI 官方 API 地址。

如果你后面要切换到别的兼容 OpenAI API 地址，再在 `.env` 里加上：

```env
OPENAI_BASE_URL=https://your-endpoint.example/v1
```

## 使用

优先通过 `.env` 改配置；例如：

```env
WHISPER_MODEL_REPO=mlx-community/whisper-large-v3-turbo
TRANSLATION_MODEL=gpt-5.4
TARGET_LANGUAGE=zh-Hans
```

如果你想用 Kotoba-Whisper，在当前这套 `mlx-whisper` 流程里，应该填 MLX 转换版仓库，例如：

```env
WHISPER_MODEL_REPO=kaiinui/kotoba-whisper-v2.0-mlx
```

这个模型卡明确给了 `mlx_whisper.transcribe(..., path_or_hf_repo="kaiinui/kotoba-whisper-v2.0-mlx")` 的用法：
<https://huggingface.co/kaiinui/kotoba-whisper-v2.0-mlx>

代码默认值仍然集中在 [src/config.py](/Users/vacabun/code/auto-trans-sub/src/config.py)：

```python
INPUT_DIR = Path("input")
MODEL_REPO = "mlx-community/whisper-large-v3-turbo"
SOURCE_LANGUAGE = "ja"
TARGET_LANGUAGE = "zh-Hans"
TRANSLATION_MODEL = "gpt-5.4"
TRANSLATION_BATCH_SIZE = 80
GENERATE_TRANSLATION = True
USE_FP16 = True
```

然后运行：

```bash
python3 trans.py
```

会在 `output/` 目录下生成：

- `xxx.ja.srt`
- `xxx.zh-Hans.srt`
- `xxx.bilingual.srt`
- `xxx.ja.segments.json`
- `translation_index.json`

## 说明

- 现在只进行一次语音识别，第二步直接对字幕文本分段做 AI 翻译，速度会比再次跑 Whisper 更合理。
- `MODEL_REPO` 现在也支持通过 `.env` 的 `WHISPER_MODEL_REPO` 灵活切换，不必再改代码。
- 如果要换成 Kotoba-Whisper，当前脚本应使用 MLX 转换后的 Hugging Face 仓库，而不是原始的 Transformers/faster-whisper 权重仓库。
- 脚本会递归扫描 `input/` 下所有受支持的音视频文件并逐个处理。
- 如果已经存在对应的日语字幕或分段 JSON，下次运行会直接复用，不再重新识别音频。
- 如果翻译文件已经存在，默认会跳过重复翻译，避免重复消耗 API。
- `translation_index.json` 会记录源文件、日语字幕、翻译字幕、双语字幕，以及该文件是否已经翻译过。
- 代码已经拆分到 `src/` 目录，`trans.py` 只保留启动入口。
- 所有日志都使用 `flush=True`，启动后会立刻打印当前进度。
- 翻译默认按批次发送，避免一次请求过大；如果字幕很多，可以适当调小 `TRANSLATION_BATCH_SIZE`。
- 脚本启动时会自动加载项目根目录下的 `.env`。
- `.env` 已加入忽略列表，不会被提交到仓库。
