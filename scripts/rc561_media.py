"""RC561 C2: generate a controlled media library for the local Jellyfin server.

Generic titles, generated posters and backdrops, and short color-bar videos. No copyrighted or downloaded media.
Movies and 2 series with seasons, with Kodi-style NFO metadata so Jellyfin needs no internet metadata lookup.
The library is deterministic (seed 561), so captures of the clients are repeatable.
Usage: rc561_media.py --out dataset/real_apps/jellyfin-media [--movies 24]
"""
import argparse
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ADJ = ['Hidden', 'Last', 'Silent', 'Bright', 'Northern', 'Golden', 'Lost', 'Wild', 'Final', 'Secret', 'Open', 'Distant']
NOUN = ['Harbor', 'Signal', 'Summit', 'River', 'Garden', 'Station', 'Island', 'Road', 'Archive', 'Season', 'Circuit', 'Valley']
GENRES = ['Drama', 'Comedy', 'Documentary', 'Adventure', 'Family', 'Mystery']
PLOT = 'A generated test title for interface validation. It has no real story.'


def font(size):
    for path in ('/System/Library/Fonts/SFNS.ttf', '/System/Library/Fonts/Helvetica.ttc'):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def art(path, title, size, hue):
    image = Image.new('RGB', size, tuple(int(c) for c in (40 + hue * 180, 60 + (1 - hue) * 120, 110 + hue * 90)))
    draw = ImageDraw.Draw(image)
    for i in range(0, size[1], max(size[1] // 12, 1)):
        draw.rectangle([0, i, size[0], i + size[1] // 48], fill=tuple(int(c * .85) for c in image.getpixel((0, 0))))
    draw.text((size[0] // 12, size[1] * 2 // 3), title, fill='white', font=font(max(size[0] // 12, 14)))
    image.save(path)


def video(path, seconds, hue):
    color = '0x%02x%02x%02x' % (int(40 + hue * 180), int(60 + (1 - hue) * 120), int(110 + hue * 90))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={color}:s=640x360:d={seconds}:r=24',
                    '-f', 'lavfi', '-i', f'sine=frequency=440:duration={seconds}', '-shortest',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(path)], check=True)


def nfo(path, tag, fields):
    body = ''.join(f'  <{k}>{v}</{k}>\n' for k, v in fields)
    path.write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<{tag}>\n{body}</{tag}>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--movies', type=int, default=24)
    args = parser.parse_args()
    rng = random.Random(561); used = set()
    def title():
        while True:
            t = f'{rng.choice(ADJ)} {rng.choice(NOUN)}'
            if t not in used:
                used.add(t); return t
    movies = args.out/'Movies'; movies.mkdir(parents=True, exist_ok=True)
    for i in range(args.movies):
        t, year, hue = title(), 2000 + rng.randint(0, 25), rng.random()
        folder = movies/f'{t} ({year})'; folder.mkdir(exist_ok=True)
        video(folder/f'{t} ({year}).mp4', 10, hue)
        art(folder/'poster.jpg', t, (400, 600), hue); art(folder/'backdrop.jpg', t, (1280, 720), hue)
        nfo(folder/f'{t} ({year}).nfo', 'movie', [('title', t), ('year', year), ('plot', PLOT), ('genre', rng.choice(GENRES)),
                                                   ('runtime', 1), ('rating', round(rng.uniform(5, 9), 1))])
    shows = args.out/'Shows'; shows.mkdir(exist_ok=True)
    for s in range(2):
        t, hue = title(), rng.random()
        folder = shows/t; folder.mkdir(exist_ok=True)
        art(folder/'poster.jpg', t, (400, 600), hue); art(folder/'backdrop.jpg', t, (1280, 720), hue)
        nfo(folder/'tvshow.nfo', 'tvshow', [('title', t), ('plot', PLOT), ('genre', rng.choice(GENRES))])
        for season in (1, 2):
            sf = folder/f'Season {season:02}'; sf.mkdir(exist_ok=True)
            for e in range(1, 7):
                name = f'{t} S{season:02}E{e:02}'
                video(sf/f'{name}.mp4', 8, (hue + e * .05) % 1)
                nfo(sf/f'{name}.nfo', 'episodedetails', [('title', f'Episode {e}: {title()}'), ('season', season), ('episode', e), ('plot', PLOT)])
                art(sf/f'{name}-thumb.jpg', f'Episode {e}', (640, 360), (hue + e * .05) % 1)
    print('movies', args.movies, 'shows', 2, 'episodes', 24, 'out', args.out)


if __name__ == '__main__':
    main()
