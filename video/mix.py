#!/usr/bin/env python3
"""Lay the music under each rendered film: -11 dB, a short fade in, a fade out over the last 2.5 seconds.

    python video/mix.py            # every silent render in video/out without a music version

Each cut starts the track where it fits: the 60s master from the top (its lift at 0:46 meets the montage),
shorter cuts later in the track so they open with energy.
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACK = HERE/'music'/'agreed-in-writing.mp3'
GAIN_DB = -11
START = {60: 0.0, 30: 24.0, 15: 46.0, 6: 46.0}


def mix(film: Path):
    seconds = int(re.search(r'-(\d+)s-', film.name)[1])
    out = film.with_name(film.stem + '-music.mp4')
    fade = 2.5 if seconds > 10 else 1.2
    audio = f"volume={GAIN_DB}dB,afade=t=in:st=0:d=0.2,afade=t=out:st={seconds - fade}:d={fade}"
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(film), '-ss', str(START[seconds]), '-t', str(seconds), '-i', str(TRACK),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', audio, '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
                    '-shortest', '-movflags', '+faststart', str(out)], check=True)
    print(out)


if __name__ == '__main__':
    for film in sorted((HERE/'out').glob('second-home-thailand-*s-*.mp4')):
        if not film.stem.endswith('-music'):
            mix(film)
