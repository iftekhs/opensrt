import tempfile
import ffmpeg
import os


def get_video_info(video_path: str) -> dict:
    probe = ffmpeg.probe(video_path)
    duration = float(probe["format"]["duration"])
    filename = os.path.basename(video_path)
    return {"filename": filename, "duration": duration}


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
        ffmpeg.run(
            stream,
            overwrite_output=True,
            quiet=True,
            capture_stdout=True,
            capture_stderr=True,
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"ffmpeg failed: {e.stderr.decode() if e.stderr else str(e)}")
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Install it with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
        )

    return output_path
