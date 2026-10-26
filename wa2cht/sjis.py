"""Shift-JIS code <-> glyph cell mapping of the WA2 font atlas, and script tokenizing."""

FIRST_TEXT_CELL = 748          # cells from here on hold the Chinese patch's characters


def kanji_cell(code):
    """Atlas cell index for a double-byte code in the kanji area, or None."""
    lead, trail = code >> 8, code & 0xFF
    if not 0x40 <= trail <= 0xFC:
        return None
    t = trail - 0x40
    if lead == 0x88:
        return 653 + t if trail >= 0x9F else None
    if 0x89 <= lead <= 0x97:
        return 842 + (lead - 0x89) * 189 + t
    if lead == 0x98:
        if trail <= 0x72:
            return 3677 + t
        if trail >= 0x9F:
            return 3633 + t
        return None
    if 0x99 <= lead <= 0x9F:
        return 3822 + (lead - 0x99) * 189 + t
    if 0xE0 <= lead <= 0xEA:
        return 5145 + (lead - 0xE0) * 189 + t
    if 0xFA <= lead <= 0xFC:
        return 7265 + (lead - 0xFA) * 189 + t
    return None


CELL2CODE = {}
for _lead in list(range(0x81, 0xA0)) + list(range(0xE0, 0xFD)):
    for _trail in range(0x40, 0xFD):
        _c = kanji_cell(_lead << 8 | _trail)
        if _c is not None and _c not in CELL2CODE:
            CELL2CODE[_c] = bytes([_lead, _trail])


def tokenize(b):
    """Split script bytes into ('cell', index, offset) / ('ch', str, offset) / ('raw', code, offset)."""
    out = []; i = 0
    while i < len(b):
        c = b[i]
        if (0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC) and i + 1 < len(b):
            code = c << 8 | b[i + 1]; cell = kanji_cell(code)
            if cell is not None and cell >= FIRST_TEXT_CELL:
                out.append(('cell', cell, i))
            else:
                try:
                    out.append(('ch', b[i:i + 2].decode('cp932'), i))
                except UnicodeDecodeError:
                    out.append(('raw', code, i))
            i += 2
        else:
            out.append(('ch', chr(c) if c < 0x80 else b[i:i + 1].decode('cp932', 'replace'), i))
            i += 1
    return out
