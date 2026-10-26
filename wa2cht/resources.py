"""Convert the Chinese text of RT_MENU / RT_DIALOG resources in place (same length).

Menu IDs are 16-bit words that can look like CJK characters, so the resource
structures are parsed and only text fields are touched. Dialog font names and
strings containing kana (left-over Japanese) are not changed.
"""
import struct
import pefile
from .textconv import conv_text


def _read_sz(buf, p):
    q = p
    while struct.unpack_from('<H', buf, q)[0] != 0:
        q += 2
    return buf[p:q].decode('utf-16-le'), p, q + 2


def _sz_or_ord(buf, p):
    w = struct.unpack_from('<H', buf, p)[0]
    if w == 0x0000:
        return None, p + 2
    if w == 0xFFFF:
        return None, p + 4
    s, a, e = _read_sz(buf, p)
    return (s, a), e


def _menuex_strings(buf):
    _, woff = struct.unpack_from('<HH', buf, 0)
    out = []

    def level(p):
        while True:
            p = (p + 3) & ~3
            p += 12                                   # dwType, dwState, uId
            flags = struct.unpack_from('<H', buf, p)[0]; p += 2
            s, a, p = _read_sz(buf, p)
            if s:
                out.append((s, a))
            if flags & 0x01:                          # popup: dwHelpId, then children
                p = ((p + 3) & ~3) + 4
                p = level(p)
            if flags & 0x80:
                return p
    level(4 + woff)
    return out


def menu_strings(buf):
    ver, hdr = struct.unpack_from('<HH', buf, 0)
    if ver == 1:
        return _menuex_strings(buf)
    out = []

    def level(p):
        while True:
            flags = struct.unpack_from('<H', buf, p)[0]; p += 2
            if not flags & 0x10:
                p += 2                                # menu id
            s, a, p = _read_sz(buf, p)
            out.append((s, a))
            if flags & 0x10:
                p = level(p)
            if flags & 0x80:
                return p
    level(4 + hdr)
    return out


def dialog_strings(buf):
    out = []
    ver, sig = struct.unpack_from('<HH', buf, 0)
    ex = ver == 1 and sig == 0xFFFF
    style = struct.unpack_from('<I', buf, 12 if ex else 0)[0]
    n = struct.unpack_from('<H', buf, 16 if ex else 8)[0]
    p = 26 if ex else 18
    _, p = _sz_or_ord(buf, p)                         # menu
    _, p = _sz_or_ord(buf, p)                         # class
    s, a, p = _read_sz(buf, p)                        # title
    out.append((s, a))
    if style & 0x40:                                  # DS_SETFONT: skip size, typeface untouched
        p += 6 if ex else 2
        _, _, p = _read_sz(buf, p)
    for _ in range(n):
        p = ((p + 3) & ~3) + (24 if ex else 18)
        _, p = _sz_or_ord(buf, p)                     # class
        t, p = _sz_or_ord(buf, p)                     # title
        if t:
            out.append(t)
        p += 2 + struct.unpack_from('<H', buf, p)[0]
    return out


def _is_japanese(s):
    return any('぀' <= ch <= 'ヿ' or 'ｦ' <= ch <= 'ﾟ' for ch in s)


def convert_resources(exe_bytes, exe_path):
    pe = pefile.PE(exe_path)
    data = bytearray(exe_bytes)
    changes = []
    for t in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        kind = pefile.RESOURCE_TYPE.get(t.id)
        if kind not in ('RT_MENU', 'RT_DIALOG'):
            continue
        for n in t.directory.entries:
            for lang in n.directory.entries:
                d = lang.data.struct
                off = pe.get_offset_from_rva(d.OffsetToData)
                buf = bytes(data[off:off + d.Size])
                for s, a in (menu_strings(buf) if kind == 'RT_MENU' else dialog_strings(buf)):
                    if _is_japanese(s):
                        continue
                    new = conv_text(s).replace('簡體中文版', '繁體中文版')
                    assert len(new) == len(s)
                    if new != s:
                        enc = new.encode('utf-16-le')
                        data[off + a:off + a + len(enc)] = enc
                        changes.append((s, new))
    return bytes(data), changes
