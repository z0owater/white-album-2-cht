"""WHITE ALBUM2 Simplified -> Traditional Chinese converter.

Usage:
    python convert.py main    "D:/Games/WHITE ALBUM2"
    python convert.py special "D:/Games/WHITE ALBUM2/Special Contents"

The new files are written next to the originals (or to --out); nothing is overwritten.
"""
import argparse
import os
import sys

from wa2cht.build import EDITIONS, build


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('edition', choices=sorted(EDITIONS), help='main = IC+CC with CK-GAL patch, special = Special Contents')
    ap.add_argument('game', help='game folder with the Simplified Chinese patch installed')
    ap.add_argument('--out', help='output folder (default: the game folder)')
    ap.add_argument('--font', default=os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts', 'msyh.ttc'),
                    help='Microsoft YaHei font file (default: the one installed with Windows)')
    ap.add_argument('--force', action='store_true', help='overwrite previously generated files')
    a = ap.parse_args()
    if not os.path.exists(a.font):
        sys.exit(f'font not found: {a.font} (pass --font)')
    for t in build(a.edition, a.game, a.out or a.game, a.font, force=a.force):
        print('wrote', t)
    exe = EDITIONS[a.edition]['out_exe']
    print(f'\nDone. Start the game with {exe}. To remove, delete the three files above.')


if __name__ == '__main__':
    main()
