import subprocess
import tempfile
import os
import ffmpeg
import numpy as np
import soundfile as sf
import noisereduce as nr


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


def extract_voice_audio(video_path: str, aggressive: bool = False, nr_strength: float = 0.75) -> str:
    fd, ffmpeg_tmp = tempfile.mkstemp(suffix="_ffmpeg.wav")
    os.close(fd)

    gate = (
        "agate=threshold=0.03:ratio=8:attack=5:release=150"
        if aggressive else
        "agate=threshold=0.015:ratio=4:attack=10:release=200"
    )

    filter_chain = ",".join([
        "pan=mono|c0=0.5*c0+0.5*c1",
        "highpass=f=80",
        "lowpass=f=8000",
        "afftdn=nf=-25",
        "equalizer=f=1000:width_type=o:width=2:g=3",
        gate,
        "loudnorm"
    ])

    result = subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-af", filter_chain,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        ffmpeg_tmp
    ], capture_output=True, text=True)

    if result.returncode != 0:
        if os.path.exists(ffmpeg_tmp):
            os.unlink(ffmpeg_tmp)
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")

    try:
        audio, rate = sf.read(ffmpeg_tmp)

        noise_sample_duration = int(rate * 1.5)
        noise_profile = audio[:noise_sample_duration]

        reduced = nr.reduce_noise(
            y=audio,
            sr=rate,
            y_noise=noise_profile,
            stationary=False,
            prop_decrease=nr_strength,
        )

        fd, final_tmp = tempfile.mkstemp(suffix="_voice.wav")
        os.close(fd)
        sf.write(final_tmp, reduced, rate)
        return final_tmp

    finally:
        if os.path.exists(ffmpeg_tmp):
            os.unlink(ffmpeg_tmp)
