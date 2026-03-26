# opensrt

A powerful CLI tool that generates `.srt` subtitle files from video files using local Whisper transcription with advanced audio processing.

## Features

- **Fully offline** — All processing happens locally, no cloud dependencies
- **Advanced audio processing** — ffmpeg + noisereduce for clean voice extraction
- **Accurate timestamps** — stable-ts provides precise word-level timing
- **VAD (Voice Activity Detection)** — Silero VAD for detecting speech boundaries
- **Dual-model mode** — Use small for accuracy + base for timestamps
- **Customizable output** — Font and color selection for subtitles
- **GPU acceleration** — Automatic CUDA detection for faster processing

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

## Quick Start

```bash
# Basic usage — generates video.srt next to video.mp4
opensrt generate video.mp4

# Use defaults (skip font/color prompts)
opensrt generate video.mp4 --withdefaults
```

## Usage

```bash
opensrt generate <video_path> [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--model` | choice | base | Whisper model (tiny, base, small, medium, large) |
| `--language` | string | auto | Language code (en, es, fr, etc.) |
| `--vad/--no-vad` | flag | enabled | Enable Silero VAD for silence detection |
| `--denoise/--no-denoise` | flag | enabled | Remove background noise (ffmpeg + noisereduce) |
| `--nr-strength` | float | 0.75 | Noise reduction strength (0.1-1.0) |
| `--gap` | float | 0.8 | Min silence gap (seconds) to split subtitles |
| `--font` | string | prompt | Font family (Arial, Tahoma, Verdana, etc.) |
| `--color` | string | prompt | Text color (White, Yellow, Green, etc.) |
| `--withdefaults` | flag | disabled | Skip font/color prompts, use defaults |

### Examples

```bash
# Specify model and language
opensrt generate video.mp4 --model small --language en

# Skip noise reduction (faster)
opensrt generate video.mp4 --no-denoise

# Stronger noise reduction
opensrt generate video.mp4 --nr-strength 0.9

# Tighter subtitle gaps (0.5s instead of 0.8s)
opensrt generate video.mp4 --gap 0.5

# Custom font and color
opensrt generate video.mp4 --font "Times New Roman" --color Yellow

# Fully automated (no prompts)
opensrt generate video.mp4 --withdefaults
```

## Model Information

On first run, the Whisper model will be downloaded automatically:

| Model  | Size  |
|--------|-------|
| tiny   | ~75MB |
| base   | ~145MB|
| small  | ~480MB|
| medium | ~1.5GB|
| large  | ~2.9GB|

### Model Selection Guide

- **tiny/base**: Fast, good for quick previews
- **small**: Best balance of speed and accuracy (recommended)
- **medium/large**: Most accurate, slower processing

## How It Works

```
video.mp4
    │
    ▼
┌─────────────────────────────────────────────┐
│ 1. Audio Extraction (ffmpeg)                │
│    - Convert to 16kHz mono WAV              │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 2. Denoising (if --denoise enabled)        │
│    - ffmpeg: frequency filtering + gate    │
│    - noisereduce: statistical subtraction  │
│    - Output: clean voice-only audio        │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 3. Transcription (stable-ts + Whisper)      │
│    - VAD: detect speech boundaries         │
│    - Transcribe with word-level timestamps  │
│    - Regroup by gap/punctuation            │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 4. SRT Generation                           │
│    - Apply font + color styling            │
│    - Write to .srt file                    │
└─────────────────────────────────────────────┘
    │
    ▼
video.srt
```

## Output

The generated `.srt` file is saved next to the input video with the same base name:
- `/videos/lecture.mp4` → `/videos/lecture.srt`

## Troubleshooting

**"ffmpeg not found" error**
- Install ffmpeg (see Prerequisites section)

**Slow transcription**
- Use `--model small` instead of medium/large
- Use `--no-denoise` if audio is already clean
- Ensure GPU is available (CUDA)

**Poor timestamp accuracy**
- Use `--denoise` to clean audio first
- Try `--gap 0.5` for tighter subtitle splitting