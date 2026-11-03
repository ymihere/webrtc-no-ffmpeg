# webrtc-no-ffmpeg

LiveKit's WebRTC library, built for Linux, Windows and macOS **without ffmpeg and without H.264**.

This is an unofficial build. It is not made or supported by LiveKit, and it comes with no promise of support.

## Why

[LiveKit's Rust SDK](https://github.com/livekit/rust-sdks) downloads a prebuilt WebRTC library. On computers that library carries ffmpeg and OpenH264 inside it. Without them:

- **No LGPL duty for ffmpeg.** Inside a static library, ffmpeg makes it hard for a closed app to meet the LGPL, which requires that people can swap ffmpeg for a changed copy.
- **No H.264 patent question.** H.264 is patent-licensed, and Cisco's patent cover for OpenH264 holds only for the binaries Cisco ships, not for a copy built from source.
- **No ffmpeg in the way.** If your app also links ffmpeg, the copy in the library can get in the way ([rust-sdks issue 1033](https://github.com/livekit/rust-sdks/issues/1033)). With none in it that clash should go; this has not been tried.

LiveKit's Android builds already leave these out, so there are none here.

## What you give up

- **H.264 does not work.** Calls can use VP8, VP9 and AV1, and nothing in this library can talk to a device that only offers H.264.
- **Other patent questions remain.** VP9 and AV1 have patent claims of their own. This is not legal advice.
- **BoringSSL is still inside.** The library's clash with OpenSSL, which LiveKit tracks separately, is not touched.

## Use it

Take the zip for your system from [Releases](../../releases) (a system built again is in a release of its own, with `-2` and so on after the first one's name, so a published zip never changes), check it against `SHA256SUMS`, unpack it, and point the SDK at the folder:

```sh
gh attestation verify webrtc-linux-x64-release.zip --repo ymihere/webrtc-no-ffmpeg   # was it built by this workflow?
LK_CUSTOM_WEBRTC=/path/to/linux-x64-release cargo build
```

**A build fits only the LiveKit version it was made from.** Each release names the commits it was built from and the `webrtc-sys-build` version it belongs to. Tested with a real call so far: Linux x64, on `webrtc-sys` 0.3.52.

| Zip | System |
|---|---|
| `webrtc-linux-x64-release.zip` | Linux, x86-64 |
| `webrtc-win-x64-release.zip` | Windows, x86-64 |
| `webrtc-mac-arm64-release.zip` | macOS, Apple silicon |
| `webrtc-mac-x64-release.zip` | macOS, Intel |

## How it is built

The [workflow](.github/workflows/build.yml) runs LiveKit's own build scripts, changed only by [`scripts/prepare.py`](scripts/prepare.py):

1. `rtc_use_h264=false`, and no `ffmpeg_branding`.
2. WebRTC pinned to an exact commit instead of a branch.

Then [`scripts/pack.py`](scripts/pack.py) looks through the finished library, its licence list and its build file for ffmpeg and OpenH264, and refuses to zip a build that names them. It also drops their header files from the zip, and refuses a zip that misses any other header of the source. If LiveKit's scripts change so that a change no longer applies, the build stops.

Each zip carries `LICENSE.md`, the licence notices of everything inside it.

## Licence

The scripts here are under the [Apache License 2.0](LICENSE). LiveKit's build scripts, which this repository changes as described above when it runs them, are also Apache-2.0. WebRTC is BSD-3-Clause, with its parts' licences listed in each zip's `LICENSE.md`.
