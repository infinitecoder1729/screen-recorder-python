# Screen Recorder
![Stars](https://img.shields.io/github/stars/infinitecoder1729/screen-recorder-python)  ![Size](https://img.shields.io/github/repo-size/infinitecoder1729/screen-recorder-python)  ![Liscence](https://img.shields.io/github/license/infinitecoder1729/screen-recorder-python)  ![Forks](https://img.shields.io/github/forks/infinitecoder1729/screen-recorder-python?style=plastic) ![visitor badge](https://visitor-badge.glitch.me/badge?page_id=infinitecoder1729.screen-recorder-python)

## A Screen Recorder built using Python

This repository now contains two scripts:
- `screen_recorder.py` — screen recording only (original).
- [`screen_recorder_with_audio.py`](https://github.com/infinitecoder1729/screen-recorder-python/blob/main/screen_recorder_with_audio.py) — screen recording + **system audio** (Windows / WASAPI loopback).

---

## 1) screen_recorder.py (Video only)

### Modules Used
1. OpenCV
2. NumPy
3. pyautogui
4. datetime

### About
Records the screen and saves an `.avi` output file with date & time in the filename.

### For User
- When the program is executed, a preview window opens which can be minimized without any hinderance to recording.
- To stop the recording you need to open the preview window and press `e`.
- Do not exit the program by crossing out the preview window or python shell as it may create a non viewable video file.

---

## 2) screen_recorder_with_audio.py (Video + system audio)

### What it does
- Records the full screen video.
- Records **system audio** (“what you hear”) using Windows WASAPI loopback.
- Automatically finds `ffmpeg` if installed, otherwise it installs a bundled FFmpeg via `imageio-ffmpeg` on first run.
- Produces a final `screen_with_audio_<timestamp>.mp4`.

> Note: This script is intended for Windows. For macOS/Linux, system-audio capture typically needs different routing/loopback setup.

### Extra modules used by this script
- `PyAudioWPatch` (WASAPI loopback capture)
- `imageio-ffmpeg` (auto-provides `ffmpeg.exe` if missing)
- `threading`, `wave`, `subprocess`, `shutil` (standard library)

### Installation

```
pip install opencv-python pyautogui numpy
pip install PyAudioWPatch
```
### Controls / Notes
- A preview window opens; you can minimize it while recording.
- To stop: focus the preview window and press `e`.
- The script may create temporary/intermediate files (e.g., `.avi` for video and `.wav` for audio) before muxing into the final `.mp4`.

---

