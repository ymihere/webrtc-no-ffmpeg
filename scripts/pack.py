#!/usr/bin/env python3
"""Checks a finished build holds no ffmpeg and no H.264 code, then zips it as LiveKit zips its own.

A build that fails any check is not zipped, so it cannot be published.

    pack.py <folder holding the build> <linux-x64-release and so on> <zip to write>
"""
import pathlib
import shutil
import sys
import zipfile

CODE_WORDS = [b"ffmpeg", b"libavcodec", b"libavformat", b"libavutil", b"openh264"]
LISTED_WORDS = [b"ffmpeg", b"openh264"]
HEADERS_TO_DROP = ["ffmpeg", "openh264"]


def found(path, words):
    data = path.read_bytes().lower()
    return [word.decode() for word in words if word in data]


def check(build):
    faults = []
    libraries = [build / "lib" / "libwebrtc.a", build / "lib" / "webrtc.lib"]
    libraries = [library for library in libraries if library.is_file()]
    if len(libraries) != 1:
        faults.append(f"expected one library in {build / 'lib'}, found {len(libraries)}")
    for library in libraries:
        if words := found(library, CODE_WORDS):
            faults.append(f"{library.name} holds {words}")
    for name, words in (("LICENSE.md", LISTED_WORDS), ("webrtc.ninja", LISTED_WORDS)):
        path = build / name
        if not path.is_file() or path.stat().st_size == 0:
            faults.append(f"{name} is missing or empty")
        elif hits := found(path, words):
            faults.append(f"{name} names {hits}")
    args = build / "args.gn"
    if not args.is_file():
        faults.append("args.gn is missing")
    else:
        settings = args.read_text().replace(" ", "")
        if "rtc_use_h264=false" not in settings:
            faults.append("args.gn does not say rtc_use_h264=false")
        if "ffmpeg_branding" in settings:
            faults.append("args.gn sets ffmpeg_branding")
    return faults


def main(parent, name, zip_path):
    build = pathlib.Path(parent) / name
    for header in HEADERS_TO_DROP:
        shutil.rmtree(build / "include" / "third_party" / header, ignore_errors=True)
    if faults := check(build):
        sys.exit("Not packed:\n  " + "\n  ".join(faults))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(build.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(build.parent).as_posix())
    print(f"{zip_path}: no ffmpeg, no H.264")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
