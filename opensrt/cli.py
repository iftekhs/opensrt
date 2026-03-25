import os
import click
from rich.console import Console

from opensrt import __version__
from opensrt import audio
from opensrt import transcribe
from opensrt import srt_writer

console = Console()

FONT_OPTIONS = ["Arial", "Tahoma", "Verdana", "Times New Roman", "Courier New", "Georgia"]
COLOR_OPTIONS = {
    "White": "#FFFFFF",
    "Yellow": "#FFFF00",
    "Green": "#00FF00",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Red": "#FF0000",
}


def prompt_font() -> str:
    console.print("\n[bold]Select subtitle font:[/bold]")
    for i, font in enumerate(FONT_OPTIONS, 1):
        console.print(f"  {i}. {font}")
    choice = click.prompt("Enter number (1-6)", type=int, default=1)
    return FONT_OPTIONS[min(max(choice, 1), len(FONT_OPTIONS)) - 1]


def prompt_color() -> str:
    console.print("\n[bold]Select subtitle color:[/bold]")
    colors = list(COLOR_OPTIONS.keys())
    for i, color in enumerate(colors, 1):
        console.print(f"  {i}. {color}")
    choice = click.prompt("Enter number (1-6)", type=int, default=1)
    return colors[min(max(choice, 1), len(colors)) - 1]


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
@click.option(
    "--vad/--no-vad",
    default=True,
    help="Enable Silero VAD for silence detection",
)
@click.option(
    "--denoise/--no-denoise",
    default=True,
    help="Remove background noise using ffmpeg + noisereduce (fast, ~10-15s for 5min video)",
)
@click.option(
    "--nr-strength",
    default=0.75,
    type=click.FloatRange(0.1, 1.0),
    help="Noise reduction strength 0.1-1.0 (default 0.75)",
)
@click.option(
    "--gap",
    default=0.8,
    type=float,
    help="Minimum silence gap in seconds to split subtitles",
)
@click.option(
    "--font",
    default=None,
    help="Font for subtitles (will prompt if not specified)",
)
@click.option(
    "--color",
    default=None,
    help="Color for subtitles (will prompt if not specified)",
)
def generate(video_path: str, model: str, language: str | None, karaoke: bool, vad: bool, denoise: bool, nr_strength: float, gap: float, font: str | None, color: str | None):
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

    if font is None:
        font = prompt_font()

    if color is None:
        color = prompt_color()

    audio_path = None
    try:
        if denoise:
            console.print("[cyan]Extracting and denoising audio (ffmpeg + noisereduce)...[/cyan]", end="\r")
            audio_path = audio.extract_voice_audio(video_path, nr_strength=nr_strength)
        else:
            console.print("[cyan]Extracting audio...[/cyan]", end="\r")
            audio_path = audio.extract_audio(video_path)

        console.print(f"[cyan]Loading model '{model}'...[/cyan]", end="\r")
        
        result = transcribe.transcribe(audio_path, model, language, vad, gap)

        output_path = os.path.splitext(video_path)[0] + ".srt"
        srt_writer.write_srt(result, output_path, karaoke, font, color)

        console.print(f"[green]Done: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    cli()
