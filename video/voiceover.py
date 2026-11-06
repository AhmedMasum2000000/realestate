#!/usr/bin/env python3
"""Cut the ElevenLabs take into its phrases, place each on the film's beats, and mix with the music.

    python video/voiceover.py     # writes video/out/*-final.mp4 for every cut

The take reads the whole script in one go (37 s); its pauses were found with silencedetect and the
phrases below are the spans between them. Music stays at -11 dB as asked; the finished mix is
normalised to -14 LUFS with peaks under -1 dBTP, the level social platforms play back at.
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOICE = HERE/'music'/'voiceover-hale.mp3'
TRACK = HERE/'music'/'agreed-in-writing.mp3'
MUSIC_DB = -11
MUSIC_START = {60: 0.0, 30: 24.0, 15: 46.0, 6: 46.0}

# Phrase spans in the take (seconds).
P = {
    'remember': (0.15, 1.55), 'door': (1.93, 2.84), 'imagine': (3.34, 5.88), 'meet': (6.36, 7.38),
    'system': (7.66, 14.75), 'one-desk': (12.78, 14.75), 'routes': (15.09, 20.65), 'homes': (20.98, 25.23),
    'writing': (25.52, 28.81), 'stay': (29.11, 32.13), 'feels': (30.43, 32.13), 'name': (32.56, 33.85), 'cta': (34.14, 36.88),
}
# Where each phrase starts in each cut (seconds into the film).
PLACE = {
    60: [('remember', 4.2), ('door', 11.2), ('imagine', 14.6), ('meet', 19.3), ('system', 22.2), ('routes', 30.6), ('homes', 36.9),
         ('writing', 42.6), ('stay', 47.6), ('name', 54.0), ('cta', 57.0)],
    30: [('remember', 4.2), ('door', 9.4), ('imagine', 12.8), ('one-desk', 17.6), ('stay', 22.7), ('name', 25.8), ('cta', 27.2)],
    15: [('remember', .3), ('door', 2.0), ('imagine', 4.4), ('one-desk', 8.8), ('name', 11.6)],
    6: [('remember', 1.0), ('name', 4.0)],
}


def mix(film: Path):
    seconds = int(re.search(r'-(\d+)s-', film.name)[1])
    fade = 2.5 if seconds > 10 else 1.2
    parts, labels = [], []
    for i, (name, at) in enumerate(PLACE[seconds]):
        a, b = P[name]
        end = min(b - a, seconds - at - .05)
        parts.append(f"[1:a]atrim={a:.3f}:{a + end:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0, end - .08):.3f}:d=0.08,"
                     f"adelay={int(at * 1000)}|{int(at * 1000)}[v{i}]")
        labels.append(f'[v{i}]')
    voice = ';'.join(parts) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,apad=whole_dur={seconds}[voice]"
    music = f"[2:a]atrim={MUSIC_START[seconds]}:{MUSIC_START[seconds] + seconds},asetpts=PTS-STARTPTS,volume={MUSIC_DB}dB,afade=t=in:d=0.2,afade=t=out:st={seconds - fade}:d={fade}[music]"
    graph = f"{voice};{music};[voice][music]amix=inputs=2:normalize=0:duration=longest,atrim=0:{seconds}"
    inputs = ['-i', str(film), '-i', str(VOICE), '-i', str(TRACK)]
    m = loudness_inputs(inputs, graph)
    final = f"{graph},loudnorm=I=-14:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true[out]"
    out = film.with_name(film.stem + '-final.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', final, '-map', '0:v', '-map', '[out]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', str(seconds), '-movflags', '+faststart', str(out)], check=True)
    print(out)


def loudness_inputs(inputs, graph):
    out = subprocess.run(['ffmpeg', '-hide_banner', *inputs, '-filter_complex', graph + ',loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return json.loads(out[out.rindex('{'):out.rindex('}') + 1])


if __name__ == '__main__':
    for film in sorted((HERE/'out').glob('second-home-thailand-*s-*.mp4')):
        if not film.stem.endswith(('-music', '-final')):
            mix(film)
