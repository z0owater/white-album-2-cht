# WHITE ALBUM2 Traditional Chinese Converter

[![繁體中文](https://img.shields.io/badge/%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-lightgrey?style=for-the-badge)](README.md)
[![English](https://img.shields.io/badge/English-0969da?style=for-the-badge)](README.en.md)

Converts an installed Simplified Chinese fan patch of *WHITE ALBUM2* to Traditional Chinese. Only the characters change (Taiwan standard); the wording stays the same.

This repo contains no game files, translation text or fonts. Everything is generated on your own computer from your copy of the game and the patch you installed. Please buy the game: [Leaf](https://leaf.aquaplus.jp/) / [AQUAPLUS](https://aquaplus.jp/). The PC release is *WHITE ALBUM2 EXTENDED EDITION*.

## Supported versions

| edition | Game | Simplified Chinese patch you need first |
|---|---|---|
| `main` | introductory chapter + closing chapter (set edition) | CK-GAL中文化小组 v2.01 (`WA2_chs.exe`, `ck-gal.pak`, `fon.pak`) |
| `special` | EXTENDED EDITION Special Contents | WhiteAlbum2SpecialCHS patch + menu translation (`WA2_Special_cn2.exe`, `script_cn.pak`, `fon.pak`) |

The character table only fits these two versions, so the tool checks the SHA-256 of the input files first and won't run if they differ.

## Usage

1. Install the Simplified Chinese patch from the table above.
2. Download `WA2-CHT-Converter.exe` from [Releases](https://github.com/z0owater/white-album-2-cht/releases/latest).
3. Run it, pick the game folder (main game, Special Contents, or a folder containing both) and press Convert. You can also drop the folder onto the exe. It takes a minute or two.
4. Start the game with `WA2_cht.exe` or `WA2_Special_cht.exe` from now on.

The exe is unsigned, so SmartScreen may block it: click "More info → Run anyway". It's built by GitHub Actions from this repo's code (see `.github/workflows/release.yml`).

### With Python

Needs Windows (for the system's Microsoft YaHei font) and Python 3.11+.

```bash
pip install -r requirements.txt
python convert.py main    "D:\Games\WHITE ALBUM2"
python convert.py special "D:\Games\WHITE ALBUM2 Special Contents"
```

`--out` sets the output folder, `--font` sets the font file, and `--force` overwrites previously generated files.

### Output files

Your existing files aren't touched; three files are added next to them:

| edition | New files | Start with |
|---|---|---|
| `main` | `WA2_cht.exe`, `ck-cht.pak`, `fot.pak` | `WA2_cht.exe` |
| `special` | `WA2_Special_cht.exe`, `script_tw.pak`, `fot.pak` | `WA2_Special_cht.exe` |

The Simplified version still works. To remove the Traditional version, delete those three files.

## How it works

- Script: decoded with the patch's own code table, segmented with jieba, then converted word by word with OpenCC (s2tw) so matches never cross word boundaries (e.g. 「不是只有」 turning into 「不是隻有」). A hand-checked override table is applied on top. Every character is still 2 bytes, so file lengths and offsets don't change.
- Font: the glyph textures (fill and outline, 40px and 24px) are redrawn with Microsoft YaHei in the original patch's style. About 30 late-added glyphs that the original patch put in the wrong cells display correctly here.
- UI: the in-game save/load screens, window menus and settings dialogs are converted too.

`data/` holds the "glyph cell → character" tables recovered from the patch fonts. It has no translation text.

## Known issues

- Text inside images (titles, menu graphics, etc.) is still Simplified.
- The untranslated Japanese main-game files bundled in the Special Contents script archive are left alone.
- Characters change, words don't: 「視頻」 won't become 「影片」. Some characters follow the OpenCC Taiwan standard, e.g. 「瞭解」, 「舞臺」.

## Credits

- *WHITE ALBUM2* © Leaf / AQUAPLUS.
- CK-GAL中文化小组: main game translation patch v2.01 (2013). The Chinese translation is entirely their work; this tool only converts characters. [Release thread](https://bbs.sumisora.net/read.php?tid=11041417)
- [WhiteAlbum2SpecialCHS](https://github.com/xhyf2666/WhiteAlbum2SpecialCHS) (xyx266617): Special Contents and menu translation (2021–2022), compiled from earlier community translations and revised.
- [OpenCC](https://github.com/BYVoid/OpenCC), [jieba](https://github.com/fxsjy/jieba).

## License

Code is MIT (see `LICENSE`). The game, translations and font aren't covered by it and aren't in this repo.
