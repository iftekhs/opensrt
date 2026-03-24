import stable_whisper


def transcribe(
    audio_path: str,
    model_name: str = "base",
    language: str | None = None,
) -> stable_whisper.WhisperResult:
    model = stable_whisper.load_model(model_name)
    result = model.transcribe(audio_path, language=language, regroup=True)
    return result
