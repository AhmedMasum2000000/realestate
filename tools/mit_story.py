#!/usr/bin/env python3
"""Build the Move In Thailand hero story: a short video, then WebP frames for the scroll player.

There is no filmed brand video yet, so by default the story is rendered from four
site photographs (coast, temple, city, home) as slow push-ins joined by crossfades.
Pass --video to use a real MP4 instead; the frame extraction is the same.

    python tools/mit_story.py                      # render the story from photos
    python tools/mit_story.py --video brand.mp4    # extract frames from a supplied video

Outputs (mit/assets is what the site build publishes):
    mit/media/move-in-thailand-story.mp4           the rendered story, also usable for social posts
    mit/assets/frames/desktop/NNN.webp             16:9 frames, 24 fps, WebP quality 85
    mit/assets/frames/mobile/NNN.webp              9:16 frames for phones
    mit/assets/frames/frames.json                  frame counts and sizes, read by the build

Needs ffmpeg with libwebp and libx264.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 24
QUALITY = 85
SCENE = 30          # frames each photo is on screen, including its crossfades
FADE = 12           # crossfade length in frames

# (source, crop box applied first to drop watermarks or empty sky, horizontal focus 0..1 for portrait crops)
SCENES = [
    ('mit/assets/coast.webp', None, 0.42),
    ('assets/properties/1.jpg', None, 0.46),
    ('assets/properties/2.jpg', None, 0.55),
    # The source photo carries another agency's watermark in the top right; the crop removes it.
    ('assets/properties/CP3302/hero.webp', (1448, 814, 0, 272), 0.56),
]
SIZES = {'desktop': (1280, 720), 'mobile': (540, 960)}


def run(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height', '-of', 'csv=p=0', str(path)],
                         capture_output=True, text=True, check=True).stdout.strip()
    width, height = out.split(',')[:2]
    return int(width), int(height)


def scene_clip(source, crop, focus, size, out):
    """One photo as a slow push-in: crop to the target shape, then zoom from 1.0 to 1.12."""
    width, height = size
    filters = []
    if crop:
        filters.append('crop=%d:%d:%d:%d' % crop)
        src_w, src_h = crop[0], crop[1]
    else:
        src_w, src_h = probe(ROOT / source)
    target = width / height
    if src_w / src_h > target:      # too wide: keep full height, crop width around the focus point
        crop_w, crop_h = int(src_h * target) // 2 * 2, src_h // 2 * 2
        x = int(max(0, min(src_w - crop_w, focus * src_w - crop_w / 2)))
        filters.append('crop=%d:%d:%d:0' % (crop_w, crop_h, x))
    else:                           # too tall: keep full width, crop height around the middle
        crop_w, crop_h = src_w // 2 * 2, int(src_w / target) // 2 * 2
        filters.append('crop=%d:%d:0:%d' % (crop_w, crop_h, (src_h - crop_h) // 2))
    # Upscale before zoompan so the push-in moves smoothly instead of stepping a pixel at a time.
    filters.append('scale=%d:%d:flags=lanczos' % (width * 4, height * 4))
    filters.append("zoompan=z='1+0.12*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=%d"
                   % (SCENE - 1, SCENE, width, height, FPS))
    filters.append('format=yuv420p')
    run('-loop', '1', '-i', str(ROOT / source), '-vf', ','.join(filters), '-frames:v', str(SCENE),
        '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', str(out))


def render_story(size, out, work):
    clips = []
    for index, (source, crop, focus) in enumerate(SCENES):
        clip = work / ('scene-%d.mp4' % index)
        scene_clip(source, crop, focus, size, clip)
        clips.append(clip)
    inputs, chain, last = [], [], '[0:v]'
    for clip in clips:
        inputs += ['-i', str(clip)]
    seconds = SCENE / FPS
    fade = FADE / FPS
    for index in range(1, len(clips)):
        offset = index * (seconds - fade)
        label = '[v%d]' % index
        chain.append('%s[%d:v]xfade=transition=fade:duration=%.4f:offset=%.4f%s' % (last, index, fade, offset, label))
        last = label
    run(*inputs, '-filter_complex', ';'.join(chain), '-map', last, '-r', str(FPS),
        '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out))


def extract_frames(video, size, out_dir):
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    width, height = size
    vf = 'fps=%d,scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d' % (FPS, width, height, width, height)
    run('-i', str(video), '-vf', vf, '-c:v', 'libwebp', '-quality', str(QUALITY), '-compression_level', '6',
        str(out_dir / '%03d.webp'))
    return sorted(out_dir.glob('*.webp'))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--video', help='use this MP4 instead of rendering the story from photos')
    args = parser.parse_args()
    frames_root = ROOT / 'mit/assets/frames'
    media = ROOT / 'mit/media'
    media.mkdir(exist_ok=True)
    manifest = {'fps': FPS, 'quality': QUALITY, 'source': 'video' if args.video else 'photos', 'sets': {}}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name, size in SIZES.items():
            if args.video:
                video = Path(args.video).resolve()
            else:
                video = media / ('move-in-thailand-story%s.mp4' % ('' if name == 'desktop' else '-vertical'))
                render_story(size, video, work)
            frames = extract_frames(video, size, frames_root / name)
            total = sum(frame.stat().st_size for frame in frames)
            manifest['sets'][name] = {'count': len(frames), 'width': size[0], 'height': size[1], 'bytes': total}
            print('%s: %d frames, %.1f MB' % (name, len(frames), total / 1e6))
    (frames_root / 'frames.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
