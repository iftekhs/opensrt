# opensrt

A CLI tool that generates `.srt` subtitle files from video files using local Whisper transcription.

## Features

- Fully offline transcription using OpenAI's Whisper model
- Accurate timestamps using stable-ts
- Clean SRT output files
- Simple CLI interface

## Prerequisites

- Python 3.10+
- ffmpeg (must be installed separately)

### Installing ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Installation

```bash
pip install opensrt
```

Or for development:
```bash
git clone <repo> && cd opensrt && pip install -e .
```

## Usage

```bash
# Basic usage — generates myvideo.srt next to myvideo.mp4
opensrt generate /path/to/myvideo.mp4

# Use a more accurate model
opensrt generate /path/to/myvideo.mp4 --model medium

# Force a language (skip auto-detect)
opensrt generate /path/to/myvideo.mp4 --model small --language en
```

## Options

- `--model`: Whisper model size (tiny, base, small, medium, large). Default: base.
- `--language`: Language code (e.g., en, es, fr). Auto-detect if not specified.

## Model Information

On first run, the Whisper model will be downloaded automatically:

| Model  | Size  |
|--------|-------|
| tiny   | ~75MB |
| base   | ~145MB|
| small  | ~480MB|
| medium | ~1.5GB|
| large  | ~2.9GB|

## Output

The generated `.srt` file is saved next to the input video with the same base name:
- `/videos/lecture.mp4` → `/videos/lecture.srt`
