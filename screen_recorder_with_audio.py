import os
import sys
import time
import wave
import shutil
import threading
import datetime
import subprocess

import numpy as np
import pyautogui
import cv2 as cv

def ensure_pip_package(pkg_name: str):
    try:
        __import__(pkg_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", pkg_name])


def ensure_ffmpeg_exe():
    # 1) Prefer system ffmpeg if already installed
    exe = shutil.which("ffmpeg")
    if exe:
        return exe

    # 2) Otherwise, install imageio-ffmpeg (bundles ffmpeg)
    ensure_pip_package("imageio_ffmpeg")  # import name
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def get_default_loopback_device(pyaudio_mod):
    """
    Closely follows PyAudioWPatch example approach:
    - Get WASAPI host API
    - Get default output device
    - If it's not already a loopback device, find matching loopback device by name
    """
    p = pyaudio_mod.PyAudio()

    try:
        wasapi_info = p.get_host_api_info_by_type(pyaudio_mod.paWASAPI)
    except OSError:
        p.terminate()
        raise RuntimeError("WASAPI not available on this system.")

    default_out = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

    if not default_out.get("isLoopbackDevice", False):
        for loopback in p.get_loopback_device_info_generator():
            if default_out["name"] in loopback["name"]:
                default_out = loopback
                break
        else:
            p.terminate()
            raise RuntimeError("Default loopback output device not found. Try: python -m pyaudiowpatch")

    return p, default_out

def main():
    if os.name != "nt":
        raise SystemExit("This script is written for Windows (WASAPI loopback).")

    # Ensure dependencies that are commonly missing on a fresh machine
    ensure_pip_package("pyaudiowpatch")

    import pyaudiowpatch as pyaudio

    dtstamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    video_path = f"screen_{dtstamp}.avi"
    audio_path = f"audio_{dtstamp}.wav"
    out_path = f"screen_with_audio_{dtstamp}.mp4"

    # ---- Setup audio recording thread
    stop_audio = threading.Event()

    def audio_worker():
        p, dev = get_default_loopback_device(pyaudio)

        channels = int(dev["maxInputChannels"]) if int(dev["maxInputChannels"]) > 0 else 2
        rate = int(dev["defaultSampleRate"]) if dev.get("defaultSampleRate") else 48000
        chunk = 1024
        fmt = pyaudio.paInt16

        wf = wave.open(audio_path, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio.get_sample_size(fmt))
        wf.setframerate(rate)

        stream = p.open(
            format=fmt,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=dev["index"],
            frames_per_buffer=chunk,
        )

        try:
            while not stop_audio.is_set():
                data = stream.read(chunk, exception_on_overflow=False)
                wf.writeframes(data)
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            wf.close()
            p.terminate()

    audio_thread = threading.Thread(target=audio_worker, daemon=True)
    audio_thread.start()

    # ---- Setup video recording
    size = pyautogui.size()  # (width, height)
    fps = 20

    video = cv.VideoWriter(
        video_path,
        cv.VideoWriter_fourcc(*"MJPG"),
        fps,
        size
    )

    print("Recording screen + system audio. Stop by pressing 'e' on the preview window.")

    try:
        while True:
            screen_shot = pyautogui.screenshot()
            frame_rgb = np.array(screen_shot)
            frame_bgr = cv.cvtColor(frame_rgb, cv.COLOR_RGB2BGR)

            video.write(frame_bgr)
            cv.imshow("Recording Preview (You can Minimize it)", frame_bgr)

            if (cv.waitKey(1) & 0xFF) == ord("e"):
                break
    finally:
        video.release()
        cv.destroyAllWindows()
        stop_audio.set()
        audio_thread.join(timeout=5)

    # Mux using ffmpeg (auto-provided if missing)
    ffmpeg_exe = ensure_ffmpeg_exe()

    # Try stream copy for video; if container/codec combo fails, fallback to H.264 encode.
    cmd_copy = [
        ffmpeg_exe, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        out_path
    ]

    cmd_reencode = [
        ffmpeg_exe, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        out_path
    ]

    try:
        subprocess.run(cmd_copy, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        subprocess.run(cmd_reencode, check=True)

    print("Saved:", out_path)


if __name__ == "__main__":
    main()
