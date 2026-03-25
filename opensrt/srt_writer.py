import os
import stable_whisper


def write_srt(result: stable_whisper.WhisperResult, output_path: str, karaoke: bool = False) -> None:
    if karaoke:
        result.to_srt_vtt(output_path, vtt=False)
    else:
        result.to_srt_vtt(output_path, vtt=False)
    print(f"Subtitles written to: {os.path.abspath(output_path)}")


# tag=('<font color="#00ff00">', '</font>')