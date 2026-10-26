"""Build the Traditional Chinese files from an installed Simplified Chinese patch."""
import hashlib
import json
import os
import re
import struct
from collections import Counter, defaultdict

import numpy as np

from . import glyphs
from .archive import Pak
from .resources import convert_resources
from .sjis import CELL2CODE, tokenize
from .textconv import JIS_FIXED, convert_tokens

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

EDITIONS = {
    # WHITE ALBUM2 (introductory chapter + closing chapter) + CK-GAL patch v2.01
    'main': dict(
        inputs={'WA2_chs.exe': '2f39343e7db7fc7e872687b1cef86d213d2e6902b22b36ef5517b7f6a115415f',
                'ck-gal.pak': '8c52fd631008221216b983e005fb379dcaf1935355a504e1c2c88afdb4e1c7e0',
                'fon.pak': '4f6630ade3a2ae0c7326b2ae3f8aa5488871b2e9fc8eb5df128247c71e7198c0'},
        exe='WA2_chs.exe', script='ck-gal.pak', font='fon.pak', table='table_main.json', text_files=None,
        out_exe='WA2_cht.exe', out_script='ck-cht.pak', out_font='fot.pak',
        renames=[(b'\0ck-gal\0', b'\0ck-cht\0'), (b'.tga\0\0fon\0', b'.tga\0\0fot\0')],
        name_offsets=[0xa0c54, 0xa0c5c, 0xa0c64], rdata=(0xa0000, 0xbca00)),
    # WHITE ALBUM2 EXTENDED EDITION Special Contents + WhiteAlbum2SpecialCHS patch (with menu exe)
    'special': dict(
        inputs={'WA2_Special_cn2.exe': '9f6b581b4d3766ec6439459f0fe56044d9c3c3fb646ebc4267de46bcd6ff6b67',
                'script_cn.pak': 'ff0e441e1a2c9fd6b4d7e62ccf92b474a736d1082b32f6c1c678f99af3bc635d',
                'fon.pak': 'b41b93168d618917056ebff354b6e42f957c9d7a9a14f42f3f265392096169ee'},
        exe='WA2_Special_cn2.exe', script='script_cn.pak', font='fon.pak', table='table_special.json',
        text_files='special_cn_files.json',
        out_exe='WA2_Special_cht.exe', out_script='script_tw.pak', out_font='fot.pak',
        renames=[(b'\0script_cn\0', b'\0script_tw\0'), (b'\0\0fon\0', b'\0\0fot\0')],
        name_offsets=[], rdata=(0x9ca00, 0xb9200)),
}

TEXTURES = {'14pt本体.tga': ('b14', 24), '14pt袋.tga': ('g14', 24), '本体80.tga': ('b80', 40), '袋影80.tga': ('g80', 40)}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check_inputs(game, ed):
    for name, digest in ed['inputs'].items():
        path = os.path.join(game, name)
        if not os.path.exists(path):
            raise SystemExit(f'missing {path} - is the Simplified Chinese patch installed?')
        if sha256(path) != digest:
            raise SystemExit(f'{name} does not match the supported patch version (SHA-256 differs); '
                             'the character table would not fit, refusing to continue.')


def _is_japanese(toks):
    return any(t[0] == 'ch' and isinstance(t[1], str) and '぀' <= t[1] <= 'ヿ' for t in toks)


def _tga_parts(raw):
    idl, cmt, it, _, cml, cmd, _, _, w, h, bpp, desc = struct.unpack_from('<BBBHHBHHHHBB', raw, 0)
    assert it == 1 and cmt == 1 and cml == 256 and cmd == 32 and bpp == 8 and idl == 0 and not desc & 0x20
    pal = np.frombuffer(raw[18:1042], np.uint8).reshape(256, 4)
    idx = np.frombuffer(raw[1042:1042 + w * h], np.uint8).reshape(h, w).copy()
    return raw[:1042], pal, idx, raw[1042 + w * h:], w


def _quantizer(pal, idx):
    used = np.unique(idx)
    white = [i for i in used if tuple(pal[i, :3]) == (255, 255, 255)]
    zero = Counter(idx.ravel().tolist()).most_common(1)[0][0]
    assert pal[zero, 3] == 0
    levels = [(int(pal[i, 3]), int(i)) for i in white] + [(0, int(zero))]
    lut = np.zeros(256, np.uint8)
    for v in range(256):
        lut[v] = min(levels, key=lambda lv: (abs(lv[0] - v), -lv[0]))[1]
    return lut


def build(edition, game, out, font_path, force=False, log=print):
    ed = EDITIONS[edition]
    check_inputs(game, ed)
    os.makedirs(out, exist_ok=True)
    targets = [os.path.join(out, ed[k]) for k in ('out_exe', 'out_script', 'out_font')]
    for t in targets:
        if os.path.exists(t) and not force:
            raise SystemExit(f'{t} already exists (use --force to overwrite)')
    glyphs.set_font(font_path)
    table = {int(k): v for k, v in json.load(open(os.path.join(DATA, ed['table']), encoding='utf-8')).items()}
    wanted = set(json.load(open(os.path.join(DATA, ed['text_files'])))) if ed['text_files'] else None

    script = Pak(os.path.join(game, ed['script']))
    font = Pak(os.path.join(game, ed['font']))
    exe_path = os.path.join(game, ed['exe'])
    exe = bytearray(open(exe_path, 'rb').read())
    sfiles = script.files()

    # text units: script files, plus the exe's in-game strings drawn with the game font
    units = [('txt', n, b) for n, b in sfiles.items() if n.endswith('.txt') and (wanted is None or n in wanted)]
    offs = list(ed['name_offsets'])
    lo, hi = ed['rdata']
    offs += [lo + m.start() for m in re.finditer(rb'<F20[^>]*>', bytes(exe[lo:hi]))]
    for off in offs:
        end = exe.index(b'>', off) + 1 if exe[off:off + 3] == b'<F2' else exe.index(0, off)
        b = bytes(exe[off:end])
        if not _is_japanese(tokenize(b)):
            units.append(('exe', off, b))
    log(f'text units: {sum(u[0] == "txt" for u in units)} script files, {sum(u[0] == "exe" for u in units)} exe strings')

    conv = []
    per_cell = defaultdict(Counter)
    for kind, key, b in units:
        toks = tokenize(b)
        res = convert_tokens(toks, table)
        conv.append((kind, key, b, toks, res))
        for t, r in zip(toks, res):
            if r is not None:
                per_cell[t[1]][r] += 1
    primary = {c: cnt.most_common(1)[0][0] for c, cnt in per_cell.items()}
    usage = {c: sum(cnt.values()) for c, cnt in per_cell.items()}
    tc2cell = {}
    for c in sorted(primary, key=lambda c: -usage[c]):
        tc2cell.setdefault(primary[c], c)

    # Traditional forms that no existing cell shows get unused cells of the Japanese kanji area
    busy = {t[1] for t in tokenize(bytes(exe)) if t[0] == 'cell'}
    for n, b in sfiles.items():
        if n.endswith('.txt'):
            busy |= {t[1] for t in tokenize(b) if t[0] == 'cell'}
    free = [c for c in range(4400, 7136) if c in CELL2CODE and CELL2CODE[c][1] != 0x7F
            and c not in busy and c not in JIS_FIXED and c not in primary]
    alloc, disp, newbytes = {}, dict(primary), {}
    for kind, key, b, toks, res in conv:
        nb = bytearray(b)
        for t, r in zip(toks, res):
            if r is None:
                continue
            if primary[t[1]] == r:
                target = t[1]
            elif r in tc2cell:
                target = tc2cell[r]
            else:
                if r not in alloc:
                    alloc[r] = free.pop(0); disp[alloc[r]] = r; tc2cell[r] = alloc[r]
                target = alloc[r]
            nb[t[2]:t[2] + 2] = CELL2CODE[target]
        newbytes[(kind, key)] = bytes(nb)
    log(f'{len(primary)} cells used, {len(alloc)} extra cells for Traditional variants')

    for kind, key, b, toks, res in conv:                        # self-check
        nb = newbytes[(kind, key)]
        assert len(nb) == len(b)
        for t0, t1, r in zip(toks, tokenize(nb), res):
            assert (t0 == t1) if r is None else (t1[0] == 'cell' and disp[t1[1]] == r), (key, t0, t1, r)

    # redraw every cell the converted text shows
    cells = sorted(disp)
    rendered = {c: glyphs.render(disp[c]) for c in cells}
    newtex = {}
    for name, (layer, size) in TEXTURES.items():
        head, pal, idx, tail, w = _tga_parts(font.read(name))
        lut = _quantizer(pal, idx)
        top = idx[::-1].copy()
        cols = w // size
        for c in cells:
            r, q = divmod(c, cols)
            top[r * size:(r + 1) * size, q * size:(q + 1) * size] = \
                lut[np.clip(np.rint(rendered[c][layer]), 0, 255).astype(np.uint8)]
        newtex[name] = head + top[::-1].tobytes() + tail
    log(f'{len(cells)} glyphs drawn')

    script.write(targets[1], {k: v for (kind, k), v in newbytes.items() if kind == 'txt'})
    font.write(targets[2], newtex)
    for (kind, off), v in newbytes.items():
        if kind == 'exe':
            exe[off:off + len(v)] = v
    for old, new in ed['renames']:
        assert len(old) == len(new) and bytes(exe).count(old) == 1, old
        i = bytes(exe).index(old)
        exe[i:i + len(new)] = new
    exe, changes = convert_resources(bytes(exe), exe_path)
    log(f'{len(changes)} menu/dialog strings converted')
    with open(targets[0], 'wb') as f:
        f.write(exe)
    return targets
