# 附錄 C：疑難排解（含三平台差異）

卡住的時候先看這裡。每一項都是「症狀 → 原因 → 解法」。

---

## 0. 萬用診斷三連

任何環境問題，先跑這三行，八成能直接看出原因：

```bash
python3 --version                                   # 版本對嗎
python3 -c "import sys; print(sys.executable)"      # 用的是哪個 Python
python3 -m pip list                                 # 這個 Python 裝了什麼
```

在 Jupyter 裡跑這格：

```python
import sys, platform
print(sys.version.split()[0])
print(sys.executable)
print("虛擬環境：", sys.prefix != sys.base_prefix)
print(platform.system())
```

---

## 1. 安裝與版本

### `python: command not found` / 開啟 Microsoft Store

| 平台 | 原因 | 解法 |
| --- | --- | --- |
| 🪟 | `python` 被商店捷徑劫持 | **用 `py -3`**，或安裝時勾選「Add python.exe to PATH」 |
| 🍎🐧 | 只有 `python3` 沒有 `python` | 用 `python3`（這是正常的） |

**本教材凡是寫 `python3` 的地方，Windows 使用者一律改成 `py -3`。**

### 版本太舊（`SyntaxError` 在很正常的語法上）

```python
x: int | None = None       # 需要 3.10+
match 值: ...              # 需要 3.10+
Counter(...).total()       # 需要 3.10+
```

看到這些語法報 `SyntaxError`，先確認版本 ≥ 3.10。

### 🐧 `error: externally-managed-environment`

```
× This environment is externally managed
```

新版 Debian/Ubuntu 禁止你往系統 Python 裝套件（**這是保護你**）。

✅ **解法：建虛擬環境**，不要用 `--break-system-packages`。

```bash
sudo apt install python3-venv
python3 -m venv .venv && source .venv/bin/activate
```

---

## 2. 找不到模組

### `ModuleNotFoundError: No module named 'pandas'`（第三方套件）

**原因永遠是：pip 裝到 A 環境，Python 跑在 B 環境。**

```bash
# 診斷
python3 -c "import sys; print(sys.executable)"
which pip        # 🪟 where pip
```

✅ **解法：用 `-m` 安裝，保證裝對地方**

```bash
python3 -m pip install pandas
```

✅ **在 Jupyter 裡**

```python
import sys
!{sys.executable} -m pip install pandas
```

### `ModuleNotFoundError: No module named 'drinkshop'`（自己的套件）

| 原因 | 解法 |
| --- | --- |
| 從錯誤的目錄執行 | `cd 專案根目錄` 再跑 |
| 用 `python3 套件/模組.py` | 改用 `python3 -m 套件.模組` |
| 沒安裝 | `python3 -m pip install -e .` |
| Notebook | `sys.path.insert(0, str(專案根目錄))`（別寫死絕對路徑） |
| 缺 `__init__.py` | 加一個空檔案 |

### `AttributeError: module 'json' has no attribute 'load'`

你有一個自己寫的 `json.py`（或 `random.py`、`csv.py`、`test.py`…）蓋掉了標準庫。

✅ 改檔名，並刪掉 `__pycache__/`。

---

## 3. Jupyter

### Notebook 裡 `import` 失敗，但終端機可以

kernel 用的不是你 `pip install` 的那個 Python。

```python
import sys; print(sys.executable)      # 在 Notebook 裡跑，看是哪個
```

✅ 把虛擬環境註冊成 kernel：

```bash
source .venv/bin/activate
python3 -m pip install ipykernel
python3 -m ipykernel install --user --name=專案名 --display-name "Python (專案名)"
```

然後在 Notebook 右上角切換 kernel。

### 改了 `.py` 檔，Notebook 沒反應

模組已經被載入，不會自動重載。

```python
%load_ext autoreload
%autoreload 2
```

或直接 **Restart Kernel**（最可靠）。

### `NameError` 但那個變數明明有定義

**那一格沒有執行過**，或者你的執行順序跳來跳去。

✅ `Run → Restart Kernel and Run All Cells`。
`In [7]` 那個數字是「第幾個被執行的」，不是「第幾格」。

### 程式跑不完 / 卡住

| 可能 | 處理 |
| --- | --- |
| 無窮迴圈 | 按 `I` 兩下或工具列 ■ 中斷 |
| 用了 `input()` | 上方會有輸入框；自動化執行時會卡死，改用參數 |
| 用了 `breakpoint()` | 同上，Notebook 裡不建議用 |
| 真的很慢 | 先用小資料測，`%timeit` 量一下 |

### Notebook 打不開 / token 錯誤

複製終端機印出的完整網址（含 `?token=...`）貼到瀏覽器。
或 `jupyter lab --no-browser` 之後手動複製。

---

## 4. 中文與編碼 ⚠️ 最常見

### `UnicodeDecodeError: 'cp950' codec can't decode byte...`

🪟 Windows 預設編碼是 cp950（Big5），你在讀一個 UTF-8 檔案。

✅ **明確指定編碼（每次都要）**

```python
open(路徑, encoding="utf-8")
Path(路徑).read_text(encoding="utf-8")
```

### 讀出來是亂碼（但沒報錯）

`ç­è¨` 這種 → 用錯編碼解讀，而且剛好沒報錯。**這比報錯更危險。**

✅ 同上，明確指定 `encoding="utf-8"`。
如果來源真的是 Big5（舊系統匯出的），用 `encoding="cp950"` 讀進來，
然後**一律用 UTF-8 存出去**。

### Excel 開 CSV 中文變亂碼

Excel 不會猜 UTF-8。

✅ 存檔時用 `encoding="utf-8-sig"`（加上 BOM）。

### CSV 每列之間多一個空行（🪟）

寫檔時忘了 `newline=""`。

```python
with open(路徑, "w", encoding="utf-8", newline="") as f:      # ✅
```

### JSON 檔裡的中文變成 `\u73cd\u73e0`

```python
json.dump(物件, f, ensure_ascii=False, indent=2)      # ✅
```

### 🪟 `UnicodeEncodeError: 'charmap' codec can't encode characters`

**注意這個和前面幾個不一樣：它不是「讀檔」出問題，是 `print` 出問題。**

```
  File "run_tests.py", line 90, in main
    print("  drinkshop 測試套件（不需要 pytest）")
  File "...\encodings\cp1252.py", line 19, in encode
UnicodeEncodeError: 'charmap' codec can't encode characters in position 12-19
```

Windows 的**標準輸出**預設不是 UTF-8（可能是 cp950 或 cp1252），
所以 `print` 一個中文字串就會炸掉。**你的程式邏輯完全沒問題，是輸出管道的編碼問題。**

> 🔍 **這是真實發生過的事故。**
> 這份教材第一次在 Windows 上驗證時，`examples/run_tests.py` 和
> `tools/build_notebooks.py` 全部死在這裡 —— 而 macOS 和 Linux 上完全正常。
> **這就是為什麼「在我電腦上可以跑」不能算數。**
>
> 想在 macOS / Linux 上模擬這個情境，不必真的找一台 Windows：
>
> ```bash
> PYTHONIOENCODING=cp1252 python3 你的程式.py
> ```

✅ **解法一：程式自己處理（推薦，使用者什麼都不用做）**

```python
import sys

def use_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):          # Python 3.7+
            stream.reconfigure(encoding="utf-8", errors="replace")

use_utf8_stdout()
```

放在**做輸出的那一層**（CLI 的 `main()`、工具腳本的開頭）就好，
其他模組完全不需要知道這件事 —— 又是一次「把副作用推到邊界」。

實際例子見 `examples/drinkshop/cli.py` 和 `examples/run_tests.py`。

✅ **解法二：環境變數（CI 裡最方便）**

```powershell
$env:PYTHONUTF8 = "1"           # 讓 Python 全面使用 UTF-8
$env:PYTHONIOENCODING = "utf-8"
```

```yaml
# GitHub Actions
env:
  PYTHONUTF8: "1"
```

✅ **解法三：切換主控台代碼頁**

```powershell
chcp 65001
```

或直接用 Windows Terminal / VS Code 的終端機（預設就支援 UTF-8）。

### 🪟 git 說檔案被改了，但我什麼都沒改

**這是同一起事故的第二幕**，原因有兩個，兩個都要修：

**原因一：程式寫檔時產生了 CRLF**

Python 的文字模式在 Windows 上會把 `\n` 自動換成 `\r\n`。
所以同一份來源，在 Mac 上產生 LF、在 Windows 上產生 CRLF，git 就認為檔案不一樣。

```python
# ✖ 在 Windows 上會寫出 CRLF
路徑.write_text(內容, encoding="utf-8")

# ✔ 明確指定，三平台一致
路徑.write_text(內容, encoding="utf-8", newline="\n")
```

⚠️ 很多函式庫的 `write()` 都有這個問題（`nbformat.write` 就是），
遇到時自己用 `writes()` 拿到字串再自己寫檔。

**原因二：git 的 autocrlf**

Windows 的 git 預設 `core.autocrlf=true`：checkout 時把 LF 換成 CRLF。

✅ **解法：專案根目錄放一個 `.gitattributes`**

```
* text=auto eol=lf
```

這是第 9 章的換行差異在版本控制層面的版本，一行設定解決。

---

## 5. 路徑

### `FileNotFoundError` 但檔案明明在那裡

| 原因 | 解法 |
| --- | --- |
| 相對路徑是相對於「執行位置」，不是檔案位置 | 用 `Path(__file__).resolve().parent` |
| 🍎🐧 檔名大小寫不符 | Linux **區分大小寫**，`Data.csv` ≠ `data.csv` |
| 路徑裡的 `\n` 被當成換行（🪟） | 用 `r"C:\temp\new"` 或 `Path()` |
| 前後有空白 | `路徑.strip()` |

```python
# 診斷
p = Path("資料/訂單.csv")
print(p.resolve())        # 它實際指向哪裡
print(Path.cwd())         # 你現在在哪
print(list(p.parent.iterdir()))    # 那個資料夾裡到底有什麼
```

### `PermissionError`

| 原因 | 解法 |
| --- | --- |
| 🪟 檔案被 Excel 開著 | 關掉 Excel |
| 目標是資料夾不是檔案 | 檢查路徑 |
| 沒有寫入權限 | 改寫到自己的目錄，或 🐧 檢查 `ls -l` |

### `FileExistsError`

用了 `"x"` 模式，或 `mkdir()` 沒加 `exist_ok=True`。

```python
Path("資料").mkdir(parents=True, exist_ok=True)     # ✅
```

---

## 6. 常見錯誤訊息對照

| 訊息 | 意思 | 常見原因 |
| --- | --- | --- |
| `NameError: name 'x' is not defined` | 用了不存在的名字 | 拼字錯；Notebook 那格沒執行；忘了 `self.` |
| `SyntaxError: invalid syntax` | 語法錯 | 少冒號、少括號、`=` 與 `==` 搞混 |
| `IndentationError` | 縮排錯 | 多／少縮排 |
| `TabError` | Tab 與空格混用 | 編輯器設定成「Tab 轉 4 空格」 |
| `TypeError: can only concatenate str...` | 字串 + 數字 | 用 f-string |
| `TypeError: 'NoneType' object is not ...` | 拿到 `None` | 函式忘了 `return`；`.sort()` 回傳 `None` |
| `TypeError: unhashable type: 'list'` | list 當成字典的鍵 | 改用 tuple |
| `ValueError: invalid literal for int()` | 字串內容不是數字 | 先 `.strip()`，或用 try/except |
| `KeyError: 'x'` | 字典沒這個鍵 | 用 `.get(鍵, 預設)`；檢查有沒有空白／錯字 |
| `IndexError: list index out of range` | 索引超出範圍 | 最後一個是 `len-1`；檢查空清單 |
| `AttributeError: 'X' has no attribute 'y'` | 物件沒這個屬性 | 拼字錯；型別不是你以為的那個 |
| `ZeroDivisionError` | 除以零 | **空清單算平均** ← 最常見 |
| `UnboundLocalError` | 函式裡想改外面的變數 | 改用參數 + `return`，別用 `global` |
| `RecursionError` | 遞迴太深 | 檢查終止條件 |
| `ModuleNotFoundError` | 找不到模組 | 見第 2 節 |

**讀 traceback 的方法：從最後一行往上讀。** 最後一行說「發生什麼」，上面說「在哪裡」。

---

## 7. 測試

### `pytest` 找不到我的套件

```
ModuleNotFoundError: No module named 'drinkshop'
```

✅ 三個解法（擇一）：

1. 在專案根目錄放一個 `conftest.py`（見 `examples/conftest.py`）
2. `python3 -m pip install -e .`
3. `python3 -m pytest`（用 `-m` 會把目前目錄加進 `sys.path`）

### 測試在我電腦過，在別人電腦掛

| 症狀 | 原因 |
| --- | --- |
| 只有 Windows 掛 | 編碼、路徑分隔符、`newline=""` |
| 只有 Linux 掛 | 檔名大小寫 |
| 週末掛、平日過 | 測試裡用了 `date.today()` |
| 有時過有時掛 | 用了 `random` 沒固定種子；測試之間互相影響 |
| 第一次過、第二次掛 | 測試留下了檔案／共用了狀態 |

✅ **通則：把時間、亂數、路徑都變成參數；用 `tempfile` 而不是固定路徑。**

### `assert` 沒有作用

```bash
python3 -O 程式.py       # -O 會把所有 assert 拿掉！
```

⚠️ **所以 `assert` 只能用在測試和開發期的檢查，不能用來做正式的輸入驗證。**
正式驗證要用 `if ... raise`。

### unittest 在 Jupyter 裡直接結束 kernel

```python
unittest.main(argv=[""], exit=False)      # ✅ 兩個參數缺一不可
```

---

## 8. 效能

| 症狀 | 檢查 |
| --- | --- |
| 迴圈很慢 | 有沒有巢狀迴圈？能不能先建字典？ |
| `x in 清單` 很慢 | 改用 `set`（快幾千倍） |
| 字串越接越慢 | 用 `"".join(清單)` 取代 `+=` |
| 讀大檔案記憶體爆 | 逐行讀，不要 `f.read()` |
| 同樣的計算重複很多次 | `functools.lru_cache`（只能用在純函式） |

```python
%timeit 運算式          # Jupyter 裡量時間
```

---

## 9. 三平台差異總表

| 項目 | 🪟 Windows | 🍎 macOS | 🐧 Linux |
| --- | --- | --- | --- |
| 執行 Python | `py -3` | `python3` | `python3` |
| 啟動 venv | `.venv\Scripts\activate` | `source .venv/bin/activate` | 同 macOS |
| 路徑分隔 | `\` | `/` | `/` |
| 預設編碼 | **cp950** | UTF-8 | UTF-8 |
| 換行 | `\r\n` | `\n` | `\n` |
| 檔名大小寫 | 不分 | 預設不分 | **區分** |
| 暫存目錄 | `%TEMP%` | `/tmp` | `/tmp` |
| 中文字型（matplotlib） | Microsoft JhengHei | PingFang HK | Noto Sans CJK TC（要先裝） |
| 系統 Python | 沒有 | 有（別動） | 有（**千萬別動**） |

**只要遵守這三條，上面九成的差異你都不用理會：**

1. 路徑一律用 `pathlib.Path`
2. 讀寫文字檔一律寫 `encoding="utf-8"`
3. 暫存檔一律用 `tempfile` 或 pytest 的 `tmp_path`

---

## 10. 還是解決不了

1. **把錯誤訊息的最後一行原封不動貼到搜尋引擎**（把你的檔名、路徑換成一般化的字眼）
2. **做一個最小重現範例**：把程式砍到剩下 10 行還能重現問題
   —— 通常砍到一半你就自己找到原因了
3. **寫一個測試把它釘死**，修好之後留著（第 11 章的回歸測試）
4. 官方文件：<https://docs.python.org/zh-tw/3/>（有正體中文）
