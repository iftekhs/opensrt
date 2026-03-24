import tempfile
import ffmpeg
import os


def extract_audio(video_path: str) -> str:
    fd, output_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    try:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            vn=None,
            acodec="pcm_s16le",
            ar=16000,
            ac=1,
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
    except ffmpeg.Error as e:
        raise RuntimeError(f"ffmpeg failed: {e.stderr.decode() if e.stderr else str(e)}")
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Install it with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
        )

    return output_path
