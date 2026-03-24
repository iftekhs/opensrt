import os
import click
from rich.console import Console

from opensrt import __version__
from opensrt import audio
from opensrt import transcribe
from opensrt import srt_writer

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.argument("video_path", type=click.Path(exists=True))
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
def generate(video_path: str, model: str, language: str | None):
    if not os.path.isfile(video_path):
        raise click.BadParameter(f"File not found: {video_path}")

    audio_path = None
    try:
        console.print(f"[cyan]Extracting audio from video...[/cyan]")
        audio_path = audio.extract_audio(video_path)

        console.print(
            f"[cyan]Loading model '{model}' (downloads on first use)...[/cyan]"
        )
        with console.status("[cyan]Transcribing...[/cyan]"):
            result = transcribe.transcribe(audio_path, model, language)

        output_path = os.path.splitext(video_path)[0] + ".srt"
        srt_writer.write_srt(result, output_path)

        console.print(f"[green]Success! Created {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    cli()
