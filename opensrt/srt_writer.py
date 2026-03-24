import os
import stable_whisper


def write_srt(result: stable_whisper.WhisperResult, output_path: str, karaoke: bool = False) -> None:
    result.to_srt_vtt(output_path, vtt=False, karaoke=karaoke)
    print(f"Subtitles written to: {os.path.abspath(output_path)}")
