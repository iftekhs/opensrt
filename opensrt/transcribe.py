import os
import subprocess
import torch
import stable_whisper

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def get_gpu_name() -> str:
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(0)
    return "None"


def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"


def transcribe(
    audio_path: str,
    model_name: str = "base",
    language: str | None = None,
    vad: bool = True,
    gap_threshold: float = 0.8,
) -> stable_whisper.WhisperResult:
    device = get_device()
    model = stable_whisper.load_model(model_name, device=device)

    result = model.transcribe(
        audio_path,
        language=language,
        regroup=False,
        verbose=False,
        vad=vad,
    )

    (result
        .split_by_gap(gap_threshold)
        .merge_by_gap(0.2, max_words=3)
        .split_by_punctuation([('.', ' '), '?', '!', '。', '？'])
    )

    return result
