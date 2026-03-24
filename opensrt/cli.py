import os
import click
from rich.console import Console

from opensrt import __version__
from opensrt import audio
from opensrt import transcribe
from opensrt import srt_writer

console = Console()


def format_duration(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def get_video_info(video_path: str) -> dict:
    try:
        info = audio.get_video_info(video_path)
        return {
            "filename": info["filename"],
            "duration": format_duration(info["duration"]),
        }
    except Exception:
        return {
            "filename": os.path.basename(video_path),
            "duration": "Unknown",
        }


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.argument("video_path")
@click.option(
    "--model",
    default="base",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Whisper model size",
)
@click.option(
    "--language",
    default=None,
    help="Language code (e.g., en, es, fr). Auto-detect if not specified.",
)
@click.option(
    "--karaoke",
    is_flag=True,
    default=False,
    help="Generate karaoke-style subtitles with progressive highlighting.",
)
def generate(video_path: str, model: str, language: str | None, karaoke: bool):
    if not os.path.isfile(video_path):
        cwd_path = os.path.join(os.getcwd(), os.path.basename(video_path))
        if os.path.isfile(cwd_path):
            video_path = cwd_path
        else:
            raise click.BadParameter(f"File not found: {video_path}")

    video_info = get_video_info(video_path)
    device = transcribe.get_device()
    gpu_name = transcribe.get_gpu_name()
    lang_display = language if language else "Auto-detect"

    console.print("")
    console.print("==================")
    console.print(f"File: {video_info['filename']}")
    console.print(f"Duration: {video_info['duration']}")
    console.print(f"Language: {lang_display}")
    console.print(f"Using: {device.upper()} ({gpu_name})")
    console.print("==================")
    console.print("")

    audio_path = None
    try:
        console.print("[cyan]Extracting audio...[/cyan]", end="\r")
        audio_path = audio.extract_audio(video_path)

        console.print(f"[cyan]Loading model '{model}'...[/cyan]", end="\r")
        result = transcribe.transcribe(audio_path, model, language)

        output_path = os.path.splitext(video_path)[0] + ".srt"
        srt_writer.write_srt(result, output_path, karaoke)

        console.print(f"[green]Done: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    cli()
