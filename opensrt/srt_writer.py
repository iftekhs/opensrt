import os
import stable_whisper

COLOR_HEX_MAP = {
    "White": "#FFFFFF",
    "Yellow": "#FFFF00",
    "Green": "#00FF00",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Red": "#FF0000",
}


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(result: stable_whisper.WhisperResult, output_path: str, karaoke: bool = False, font: str = "Arial", color: str = "White") -> None:
    if karaoke:
        result.to_srt_vtt(output_path, vtt=False, word_level=True, tag=('<font color="#00FF00">', '</font>'))
    else:
        color_hex = COLOR_HEX_MAP.get(color, "#FFFFFF")
        lines = []
        for i, segment in enumerate(result, 1):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()
            if font or color:
                font_attrs = []
                if font:
                    font_attrs.append(f'face="{font}"')
                if color:
                    font_attrs.append(f'color="{color_hex}"')
                text = f'<font {" ".join(font_attrs)}>{text}</font>'
            lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    
    print(f"Subtitles written to: {os.path.abspath(output_path)}")
