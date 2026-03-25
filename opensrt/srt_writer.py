import os
import stable_whisper


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(result: stable_whisper.WhisperResult, output_path: str, karaoke: bool = False, font: str = "Arial") -> None:
    if karaoke:
        result.to_srt_vtt(output_path, vtt=False, word_level=True, tag=('<font color="#00ff00">', '</font>'))
    else:
        lines = []
        for i, segment in enumerate(result, 1):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()
            if font:
                text = f'<font face="{font}">{text}</font>'
            lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    
    print(f"Subtitles written to: {os.path.abspath(output_path)}")
