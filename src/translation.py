import json
import os

from openai import OpenAI

from src.config import (
    TARGET_LANGUAGE,
    TRANSLATION_BATCH_SIZE,
    TRANSLATION_MODEL,
)
from src.files import log


def chunk_segments(segments, batch_size):
    for i in range(0, len(segments), batch_size):
        yield segments[i : i + batch_size]


def get_translator_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in .env or export it before running.")

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def build_translation_payload(batch):
    return [
        {
            "index": idx,
            "text": segment["text"].strip(),
        }
        for idx, segment in enumerate(batch)
    ]


def translate_batch(client, batch, batch_no, batch_total):
    payload = build_translation_payload(batch)
    prompt = (
        f"Translate the JSON array from Japanese to {TARGET_LANGUAGE}. "
        "Keep the array length unchanged. Preserve each item's index. "
        "Return JSON only with the exact schema requested. "
        "Subtitle style: concise, natural, and suitable for on-screen captions."
    )

    log(f"Translating batch {batch_no}/{batch_total} with {len(batch)} segments...")

    response = client.responses.create(
        model=TRANSLATION_MODEL,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "subtitle_translation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "index": {"type": "integer"},
                                    "translation": {"type": "string"},
                                },
                                "required": ["index", "translation"],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["items"],
                    "additionalProperties": False,
                },
            }
        },
    )

    content = json.loads(response.output_text)
    items = content["items"]
    if len(items) != len(batch):
        raise RuntimeError(
            f"Translation batch size mismatch: expected {len(batch)}, got {len(items)}"
        )

    items.sort(key=lambda item: item["index"])
    translated_batch = []
    for i, item in enumerate(items):
        if item["index"] != i:
            raise RuntimeError(
                f"Translation batch index mismatch: expected {i}, got {item['index']}"
            )
        translated_batch.append(
            {
                "start": batch[i]["start"],
                "end": batch[i]["end"],
                "text": item["translation"].strip(),
            }
        )

    return translated_batch


def translate_segments_with_ai(segments):
    client = get_translator_client()
    translated_segments = []
    batches = list(chunk_segments(segments, TRANSLATION_BATCH_SIZE))

    for batch_no, batch in enumerate(batches, start=1):
        translated_segments.extend(
            translate_batch(client, batch, batch_no=batch_no, batch_total=len(batches))
        )

    return translated_segments
