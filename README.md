# WHITE ALBUM2 繁體中文轉換工具

[![繁體中文](https://img.shields.io/badge/%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-0969da?style=for-the-badge)](README.md)
[![English](https://img.shields.io/badge/English-lightgrey?style=for-the-badge)](README.en.md)

把已經裝好的《WHITE ALBUM2》簡體中文漢化補丁轉成繁體中文。只轉字形（臺灣用字），不改用詞。

這個 repo 裡沒有遊戲檔案、譯文或字型。所有東西都是在你自己的電腦上，從你的遊戲和你裝的補丁產生出來的。請買正版：[Leaf](https://leaf.aquaplus.jp/) / [AQUAPLUS](https://aquaplus.jp/)，PC 版是《WHITE ALBUM2 EXTENDED EDITION》。

## 支援的版本

| edition | 遊戲 | 要先裝好的簡體補丁 |
|---|---|---|
| `main` | introductory chapter + closing chapter（セット版） | CK-GAL中文化小组 v2.01（`WA2_chs.exe`、`ck-gal.pak`、`fon.pak`） |
| `special` | EXTENDED EDITION Special Contents | WhiteAlbum2SpecialCHS 補丁 + 上方選單漢化（`WA2_Special_cn2.exe`、`script_cn.pak`、`fon.pak`） |

字元對照表只對得上這兩個版本，所以工具會先比對 SHA-256，不符就不跑。

## 使用方式

1. 裝好上表的簡體補丁。
2. 從 [Releases](https://github.com/z0owater/white-album-2-cht/releases/latest) 下載 `WA2-CHT-Converter.exe`。
3. 執行後選遊戲資料夾（本篇、Special Contents，或同時包含兩者的上層資料夾都行），按「轉換」。也可以直接把資料夾拖到 exe 上。大約一兩分鐘。
4. 之後用 `WA2_cht.exe` 或 `WA2_Special_cht.exe` 開遊戲。

exe 沒有簽章，SmartScreen 可能會擋，按「其他資訊 → 仍要執行」。它是 GitHub Actions 從這個 repo 的程式碼建置的（見 `.github/workflows/release.yml`）。

### 用 Python 跑

需要 Windows（要用系統的微軟雅黑）和 Python 3.11+。

```bash
pip install -r requirements.txt
python convert.py main    "D:\Games\WHITE ALBUM2"
python convert.py special "D:\Games\WHITE ALBUM2 Special Contents"
```

`--out` 指定輸出資料夾，`--font` 指定字型檔，`--force` 覆蓋之前產生的檔案。

### 產生的檔案

原本的檔案不會動，只會在旁邊多三個檔案：

| edition | 新檔案 | 啟動 |
|---|---|---|
| `main` | `WA2_cht.exe`、`ck-cht.pak`、`fot.pak` | `WA2_cht.exe` |
| `special` | `WA2_Special_cht.exe`、`script_tw.pak`、`fot.pak` | `WA2_Special_cht.exe` |

簡體版照樣能玩。不要繁體版的話，把這三個檔案刪掉就好。

## 原理

- 劇本：用補丁自己的碼表解碼，jieba 斷詞後逐詞丟給 OpenCC（s2tw），避免跨詞誤轉（例如「不是只有」變成「不是隻有」），再套一份人工檢查過的修正表。每個字還是 2 bytes，所以檔案長度和偏移都不變。
- 字型：用微軟雅黑重畫字型貼圖（本體和描邊，40px 和 24px），照原補丁的樣式。原補丁有大約 30 個後加的字放錯格子，繁體版會顯示正確。
- 介面：遊戲內的存讀檔畫面、視窗選單和設定對話框也一起轉。

`data/` 是從補丁字型還原出來的「字元格 → 字」對照表，不含譯文。

## 已知問題

- 圖片裡的字（標題、選單圖等）還是簡體。
- Special Contents 的腳本包裡夾帶的本篇日文原文（沒翻譯的部分）不動。
- 只換字不換詞，「視頻」不會變「影片」。有些字照 OpenCC 臺灣標準，例如「瞭解」「舞臺」。

## 致謝

- 《WHITE ALBUM2》© Leaf / AQUAPLUS。
- CK-GAL中文化小组：本篇漢化補丁 v2.01（2013）。中文翻譯全部是他們做的，這個工具只是轉字形。[發佈帖](https://bbs.sumisora.net/read.php?tid=11041417)
- [WhiteAlbum2SpecialCHS](https://github.com/xhyf2666/WhiteAlbum2SpecialCHS)（xyx266617）：Special Contents 漢化與上方選單漢化（2021–2022），整理自網路上既有的漢化並修訂。
- [OpenCC](https://github.com/BYVoid/OpenCC)、[jieba](https://github.com/fxsjy/jieba)。

## 授權

程式碼是 MIT（見 `LICENSE`）。遊戲、翻譯和字型不在授權範圍內，也不在這個 repo 裡。

