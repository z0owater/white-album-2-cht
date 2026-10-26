"""One-click converter: pick the game folder (or drop it on the exe) and press the button."""
import os
import queue
import sys
import threading
import traceback

from wa2cht.build import EDITIONS, build, detect

FONT = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', 'msyh.ttc')
TITLE = 'WHITE ALBUM2 繁體中文轉換'


def run(folder, log):
    """Convert every supported game found in folder; returns True on success."""
    if not os.path.exists(FONT):
        log(f'找不到微軟雅黑字型 / Microsoft YaHei not found: {FONT}')
        return False
    found = detect(folder)
    if not found:
        log('這個資料夾裡找不到已安裝簡體中文補丁的 WHITE ALBUM2。\n'
            'No WHITE ALBUM2 with the Simplified Chinese patch was found in this folder.\n'
            '需要的檔案 / needs: WA2_chs.exe + ck-gal.pak + fon.pak，或 WA2_Special_cn2.exe + script_cn.pak + fon.pak')
        return False
    ok = True
    for edition, path in found:
        ed = EDITIONS[edition]
        log(f'\n▶ {path}')
        try:
            build(edition, path, path, FONT, force=True, log=log)
            log(f'完成！請用 {ed["out_exe"]} 啟動遊戲。 Done - start the game with {ed["out_exe"]}.')
        except SystemExit as e:
            log(f'✗ {e}'); ok = False
        except Exception:
            log('✗ 發生錯誤 / error:\n' + traceback.format_exc()); ok = False
    return ok


def gui(initial=None):
    import tkinter as tk
    from tkinter import filedialog, scrolledtext

    root = tk.Tk()
    root.title(TITLE)
    root.geometry('640x420')
    msgs = queue.Queue()

    tk.Label(root, justify='left', anchor='w', wraplength=600, text=(
        '選擇已安裝簡體中文漢化補丁的遊戲資料夾（本篇或 Special Contents，或兩者的上層資料夾），然後按「轉換」。\n'
        '原有檔案不會被修改；完成後用 WA2_cht.exe / WA2_Special_cht.exe 啟動。\n'
        'Pick the game folder with the Simplified Chinese patch installed, then press Convert.')
             ).pack(fill='x', padx=10, pady=(10, 4))
    row = tk.Frame(root); row.pack(fill='x', padx=10)
    path = tk.StringVar(value=initial or '')
    tk.Entry(row, textvariable=path).pack(side='left', fill='x', expand=True)
    tk.Button(row, text='瀏覽… Browse', command=lambda: path.set(filedialog.askdirectory() or path.get())).pack(side='left', padx=4)
    go = tk.Button(root, text='轉換 Convert', width=20)
    go.pack(pady=6)
    out = scrolledtext.ScrolledText(root, height=14, state='disabled'); out.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def write(text):
        out.configure(state='normal'); out.insert('end', text + '\n'); out.see('end'); out.configure(state='disabled')

    def pump():
        while not msgs.empty():
            item = msgs.get()
            if item is None:
                go.configure(state='normal')
            else:
                write(item)
        root.after(100, pump)

    def start():
        folder = path.get().strip().strip('"')
        if not folder or not os.path.isdir(folder):
            write('請先選擇資料夾。 Choose a folder first.'); return
        go.configure(state='disabled')
        write('轉換中，大約需要一到兩分鐘… Converting, this takes a minute or two…')
        threading.Thread(target=lambda: (run(folder, msgs.put), msgs.put(None)), daemon=True).start()

    go.configure(command=start)
    pump()
    root.mainloop()


def main():
    args = [a for a in sys.argv[1:] if a]
    if args and args[0] == '--console':                 # used for testing: no window
        if sys.stdout:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.exit(0 if run(args[1], print) else 1)
    gui(args[0] if args else None)                      # a folder dropped onto the exe arrives as argv[1]


if __name__ == '__main__':
    main()
