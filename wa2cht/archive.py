"""Leaf KCAP archives (.pak) and their LZSS compression."""
import struct


def lzss_decompress(src, outsize, n=4096, init=0xFEE):
    win = bytearray(n); r = init; out = bytearray(); i = 0
    while len(out) < outsize and i < len(src):
        flags = src[i]; i += 1
        for b in range(8):
            if len(out) >= outsize or i >= len(src):
                break
            if flags & (1 << b):
                c = src[i]; i += 1
                out.append(c); win[r] = c; r = (r + 1) & (n - 1)
            else:
                lo, hi = src[i], src[i + 1]; i += 2
                pos = lo | ((hi & 0xF0) << 4)
                for k in range((hi & 0x0F) + 3):
                    c = win[(pos + k) & (n - 1)]
                    out.append(c); win[r] = c; r = (r + 1) & (n - 1)
    return bytes(out)


def lzss_literal(data):
    """A valid LZSS stream made only of literals (flag byte 0xFF + 8 bytes)."""
    out = bytearray()
    for i in range(0, len(data), 8):
        chunk = data[i:i + 8]
        out.append(0xFF if len(chunk) == 8 else (1 << len(chunk)) - 1)
        out += chunk
    return bytes(out)


class Pak:
    ENTRY = 44

    def __init__(self, path):
        self.raw = open(path, 'rb').read()
        if self.raw[:4] != b'KCAP':
            raise ValueError(f'{path} is not a KCAP archive')
        n = struct.unpack_from('<I', self.raw, 12)[0]
        self.entries = []
        for i in range(n):
            o = 16 + i * self.ENTRY
            typ, = struct.unpack_from('<I', self.raw, o)
            name = self.raw[o + 4:o + 28].split(b'\0')[0].decode('cp932', 'replace')
            off, size = struct.unpack_from('<II', self.raw, o + 36)
            self.entries.append(dict(typ=typ, name=name, off=off, size=size))

    def read(self, name):
        for e in self.entries:
            if e['name'] == name:
                blob = self.raw[e['off']:e['off'] + e['size']]
                if e['typ'] == 1:
                    usz = struct.unpack_from('<I', blob, 4)[0]
                    return lzss_decompress(blob[8:], usz)
                if e['typ'] == 0:
                    return blob
        raise KeyError(name)

    def files(self):
        return {e['name']: self.read(e['name']) for e in self.entries if e['typ'] in (0, 1)}

    def write(self, path, replace):
        """Copy this archive to path, replacing the contents of the named entries."""
        n = len(self.entries)
        table = bytearray(self.raw[:16 + self.ENTRY * n]); body = bytearray(); off = len(table)
        for k, e in enumerate(self.entries):
            o = 16 + self.ENTRY * k
            if e['typ'] not in (0, 1):                     # directory-like entries
                struct.pack_into('<I', table, o + 36, off)
                continue
            if e['name'] in replace and e['typ'] == 1:
                data = replace[e['name']]; comp = lzss_literal(data)
                assert lzss_decompress(comp, len(data)) == data
                blob = struct.pack('<II', len(comp) + 8, len(data)) + comp
            elif e['name'] in replace:
                blob = replace[e['name']]
            else:
                blob = self.raw[e['off']:e['off'] + e['size']]
            struct.pack_into('<II', table, o + 36, off, len(blob))
            body += blob; off += len(blob)
        with open(path, 'wb') as f:
            f.write(bytes(table) + bytes(body))
