#!/usr/bin/env python3
"""Changes LiveKit's build recipe before it runs: no H.264 and no ffmpeg, and the exact WebRTC commit.

Stops if a line it expects is not there, so a changed recipe can never build the wrong library quietly.

    prepare.py <rust-sdks/webrtc-sys/libwebrtc> <linux|mac|win> <webrtc commit>
"""
import pathlib
import sys

SCRIPTS = {"linux": "build_linux.sh", "mac": "build_macos.sh", "win": "build_windows.cmd"}
FFMPEG = {"linux": 'ffmpeg_branding=\\"Chrome\\"', "mac": None, "win": 'ffmpeg_branding=\\"Chrome\\"'}


def replace_once(text, old, new, where):
    if text.count(old) != 1:
        sys.exit(f"{where}: expected {old!r} once, found it {text.count(old)} times")
    return text.replace(old, new)


def main(folder, system, commit):
    folder = pathlib.Path(folder)
    script = folder / SCRIPTS[system]
    text = script.read_text()
    text = replace_once(text, "rtc_use_h264=true", "rtc_use_h264=false", script.name)
    if FFMPEG[system]:
        text = replace_once(text, FFMPEG[system], "", script.name)
    elif "ffmpeg_branding" in text:
        sys.exit(f"{script.name}: now sets ffmpeg_branding; this recipe must remove it")
    script.write_text(text)

    gclient = folder / ".gclient"
    text = gclient.read_text()
    text = replace_once(text, "webrtc.git@m150_release", f"webrtc.git@{commit}", gclient.name)
    gclient.write_text(text + f'\ntarget_os = ["{system}"]\n')


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[2] not in SCRIPTS:
        sys.exit(__doc__)
    main(*sys.argv[1:])
