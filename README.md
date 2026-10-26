# WHITE ALBUM2 繁體中文轉換工具 / Traditional Chinese conversion kit

把已安裝的《WHITE ALBUM2》**簡體中文漢化補丁**轉換成**繁體中文**（臺灣用字，不改用詞）。
本專案**不含任何遊戲檔案、譯文或字型**：轉換在你自己的電腦上，用你自己的正版遊戲與已安裝的漢化補丁產生。

Converts an installed **Simplified Chinese** fan patch of *WHITE ALBUM2* to **Traditional Chinese**
(Taiwan characters, wording unchanged). This repository contains **no game files, no translation text and no fonts**:
everything is generated locally from your own copy of the game and the patch you installed.

> **請支持正版。** 本工具只適用於你合法擁有的遊戲。請購買 Leaf / AQUAPLUS 的正版（實體版或官方發行版），例如 PC 版《WHITE ALBUM2 EXTENDED EDITION》。
>
> **Please support the official release.** This tool is only for copies you legally own — buy the game (physical or official
> release) from Leaf / AQUAPLUS, e.g. the PC *WHITE ALBUM2 EXTENDED EDITION*.
> Official sites: <https://leaf.aquaplus.jp/> · <https://aquaplus.jp/>

---

## 支援版本 / Supported setups

| `edition` | 遊戲 / Game | 需要先安裝的簡體補丁 / Required Simplified Chinese patch |
|---|---|---|
| `main` | WHITE ALBUM2 introductory chapter + closing chapter（セット版） | CK-GAL中文化小组 汉化补丁 v2.01（`WA2_chs.exe`, `ck-gal.pak`, `fon.pak`） |
| `special` | WHITE ALBUM2 EXTENDED EDITION — Special Contents | WhiteAlbum2SpecialCHS 汉化补丁 + 上方菜单汉化（`WA2_Special_cn2.exe`, `script_cn.pak`, `fon.pak`） |

工具會先檢查這些檔案的 SHA-256；版本不同就拒絕執行（字元對照表只對應這些版本）。
The tool checks the SHA-256 of those files first and refuses to run on other versions (the character table only fits these).

## 使用方法 / Usage

需要 Windows（使用系統內建的「微軟雅黑」字型）與 Python 3.11 以上。
Requires Windows (uses the bundled Microsoft YaHei font) and Python 3.11+.

```bash
pip install -r requirements.txt
python convert.py main    "D:\Games\WHITE ALBUM2"
python convert.py special "D:\Games\WHITE ALBUM2 Special Contents"
```

會在遊戲資料夾**新增**三個檔案，原有檔案完全不變 / Three files are **added** next to the originals, which are left untouched:

| edition | 新檔案 / new files | 啟動 / start with |
|---|---|---|
| `main` | `WA2_cht.exe`, `ck-cht.pak`, `fot.pak` | `WA2_cht.exe` |
| `special` | `WA2_Special_cht.exe`, `script_tw.pak`, `fot.pak` | `WA2_Special_cht.exe` |

原本的簡體版（`WA2_chs.exe` / `WA2_Special_cn2.exe`）照常可用。要移除繁體版，刪掉這三個檔案即可。
The Simplified version keeps working; delete the three files to remove the Traditional version.

## 做了什麼 / What it does

- **劇本**：依漢化補丁的自訂碼表解碼，先用 jieba 斷詞、再逐詞以 OpenCC（s2tw）轉換，避免跨詞誤轉（如「不是只有」被轉成「不是隻有」），並套用人工審閱過的修正（頭髮／發現、然後／皇后、乾淨／幹嘛、一隻手／只有…）。每個字仍是 2 位元組，檔案長度與偏移不變。
  **Script**: decoded through the patch's custom code table, segmented with jieba, converted word by word with OpenCC (s2tw)
  so phrases never match across word boundaries, plus hand-reviewed overrides. Every character stays two bytes, so file
  lengths and offsets do not change.
- **字型**：以系統的微軟雅黑重新繪製文字貼圖（本體與描邊、40px 與 24px 兩種尺寸），風格與原補丁一致。原補丁有約 30 個後加字元的字形放錯位置（如「丢瞑保帅」「目瞭口呆」），繁體版會顯示正確的字。
  **Font**: glyph atlases redrawn with your system's Microsoft YaHei in the patch's style. About 30 glyphs that the original
  patch shows wrongly (misplaced late additions) display correctly here.
- **介面**：遊戲內的存讀檔對話框，以及視窗選單與設定對話框也一併轉換（關於視窗顯示「繁體中文版」）。
  **UI**: in-game save/load dialogs and the Windows menus/dialogs are converted too.

`data/` 內是從補丁字型還原出的「字元格 → 字」對照表（不含譯文）。
`data/` holds the recovered "glyph cell → character" tables (no translation text).

## 已知限制 / Known limitations

- 圖片中的文字（標題、選單圖片等）仍為簡體。/ Text inside images is still Simplified.
- Special Contents 的腳本包裡附帶的本篇日文原文（未翻譯部分）保持原狀。/ The untranslated Japanese files bundled in the Special Contents script archive are left as they are.
- 只轉換字形，不改用詞（例如「視頻」不會改成「影片」）。部分用字依 OpenCC 臺灣標準（如「瞭解」「舞臺」）。/ Characters only; vocabulary is unchanged.

---

## 致謝 / Credits

- **遊戲 / Game** — 《WHITE ALBUM2》© Leaf / AQUAPLUS。所有遊戲內容的權利屬於原權利人。All rights to the game belong to their owners. **請購買正版支持 / Please buy the game.**
- **CK-GAL中文化小组** — 《WHITE ALBUM2 ～introductory chapter + closing chapter～》汉化补丁 v2.01（2013）。本作的中文翻譯全部出自他們之手，本工具只做字形轉換。The entire Chinese translation of the main game is their work; this kit only converts characters.
  發佈帖 / release thread: <https://bbs.sumisora.net/read.php?tid=11041417>
- **WhiteAlbum2SpecialCHS**（xyx266617）— 『WHITE ALBUM 2 EXTENDED EDITION』Special Contents 汉化补丁與上方菜单汉化（2021–2022）；其文本整合自網路上既有的漢化並加以修訂。Special Contents patch and menu translation; their text was compiled from earlier community translations and revised.
  <https://github.com/xhyf2666/WhiteAlbum2SpecialCHS>
- [OpenCC](https://github.com/BYVoid/OpenCC)、[jieba](https://github.com/fxsjy/jieba)；字型使用使用者電腦上的 Microsoft YaHei（本專案不散布字型）/ the font is read from your own Windows installation and is not distributed.

## 授權 / License

程式碼以 MIT 授權釋出（見 `LICENSE`）。遊戲、翻譯與字型不在此授權範圍內，也不包含在本專案中。
Code is MIT-licensed (see `LICENSE`). The game, the translations and the font are not covered by it and are not included.
