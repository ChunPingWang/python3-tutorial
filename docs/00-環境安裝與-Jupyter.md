# 第 0 章：環境安裝與 Jupyter

> 🎬 **情境**：阿宏把你找來，說「我想把手搖飲店的帳務電腦化」。你點頭答應，打開筆電，然後——
> 第一個問題不是「怎麼寫程式」，而是「程式要在哪裡跑」。

這章是全書唯一一章沒有 Python 語法的。它處理的是初學者放棄率最高的一關：**環境**。
讀完你會有三樣東西：能跑的 Python、能跑的 Jupyter、以及「出事時知道去哪看」的判斷力。

---

## 0.1 你需要的三個東西

| 東西 | 做什麼 | 類比 |
| --- | --- | --- |
| **Python 直譯器** | 真正執行你程式的引擎 | 汽車引擎 |
| **編輯器或 Jupyter** | 你寫程式的地方 | 駕駛座 |
| **終端機** | 下指令給電腦的地方 | 儀表板 |

初學者常把這三個搞混，於是出現「我裝了 VS Code 為什麼還是不能跑 Python」這種問題。
**VS Code 是駕駛座，沒有引擎照樣不會動。**

---

## 0.2 安裝 Python（三平台）

本教材需要 **Python 3.10 以上**，建議 3.12 或 3.13。

### 🪟 Windows

到 [python.org/downloads](https://www.python.org/downloads/) 下載安裝檔，執行時**務必勾選**：

```
☑ Add python.exe to PATH        ← 沒勾這個,後面每一步都會失敗
```

安裝完成後打開 **PowerShell**（開始選單搜尋 `powershell`），輸入：

```powershell
py -3 --version
```

看到 `Python 3.12.x` 就成功了。

> ⚠️ **Windows 專屬：`py` 才是正解。**
> Windows 安裝 Python 時會附一個叫 `py` 的啟動器（Python Launcher）。它會自動找到你電腦上的 Python，
> 而 `python` 這個指令在 Windows 上可能被微軟商店的假捷徑劫持，打下去只會跳出商店頁面。
> **本教材凡是寫 `python3` 的地方，Windows 使用者請改成 `py -3`。**

### 🍎 macOS

macOS 內建的 `/usr/bin/python3` 版本太舊而且不該動它。請用 [Homebrew](https://brew.sh/)：

```bash
# 若還沒有 Homebrew,先裝它(官網那行指令)
brew install python@3.12
python3 --version
```

或直接到 [python.org/downloads](https://www.python.org/downloads/) 下載 `.pkg` 安裝檔，兩種都可以。

### 🐧 Linux（Ubuntu / Debian 系）

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

> ⚠️ **Linux 使用者注意**：`apt` 這類系統工具本身就是用系統 Python 寫的。
> 千萬不要 `sudo pip install` 往系統 Python 裡塞套件，那會弄壞你的作業系統工具。
> 一律用下一節的虛擬環境。

---

## 0.3 虛擬環境：每個專案一個乾淨的房間

### 😩 不用虛擬環境會怎樣

假設你直接把所有套件裝進系統 Python：

- A 專案需要 `pandas 1.5`，B 專案需要 `pandas 2.2` → 兩個不能共存，你只能二選一
- 你裝壞了某個套件 → 整台電腦的 Python 都受影響
- 你要把程式交給同事 → 你說不清楚到底該裝哪些東西

### 💡 虛擬環境就是「這個專案專屬的 Python」

它其實只是一個資料夾，裡面放著一份獨立的套件清單。刪掉它，一切回到原狀，零風險。

```bash
# 進到教材資料夾
cd python3-tutorial

# 建立(只要做一次)
python3 -m venv .venv          # 🍎🐧
py -3 -m venv .venv            # 🪟

# 啟動(每次開新終端機都要做)
source .venv/bin/activate      # 🍎🐧
.venv\Scripts\activate         # 🪟 PowerShell

# 成功的標誌:提示字元前面多出 (.venv)
(.venv) $
```

啟動之後：

```bash
pip install -r requirements.txt
```

離開用 `deactivate`。

> 🔍 **怎麼確認我現在用的是哪個 Python？**
> 這是所有環境問題的萬用診斷指令：
>
> ```bash
> python3 -c "import sys; print(sys.executable)"
> ```
>
> 如果印出來的路徑裡有 `.venv`，代表你在虛擬環境裡，正確。
> 如果印出 `/usr/bin/python3` 或 `C:\Python312\`，代表你沒啟動成功。

---

## 0.4 Jupyter Notebook：為什麼初學者特別適合

### 🎬 情境

你寫了 30 行程式算營收，執行後發現數字不對。問題在第幾行？
用 `.py` 檔的話，你得從頭再跑一次，中間插 `print` 慢慢找。

Jupyter 讓你把程式切成一格一格（cell），**每格單獨執行、立刻看到結果，而且變數會留在記憶體裡**。
你可以執行第 1 格、看結果、改第 2 格、再執行，像在跟程式對話。

| | `.py` 腳本 | Jupyter Notebook |
| --- | --- | --- |
| 執行單位 | 整個檔案 | 一格一格 |
| 看中間結果 | 要自己 `print` | 最後一行自動顯示 |
| 適合 | 正式程式、要交付的工具 | 學習、探索資料、畫圖 |
| 檔案格式 | 純文字，好比對 | JSON，版本控制較麻煩 |

**本教材的建議：第 1~12 章用 Jupyter 學，第 13 章之後學會怎麼把它變成正式的 `.py` 專案。**

### 啟動

```bash
# 確認已啟動虛擬環境,且裝好 requirements.txt
jupyter lab
```

瀏覽器會自動打開。若沒有，複製終端機裡那個 `http://localhost:8888/lab?token=...` 網址貼到瀏覽器。

### 必學的 5 個操作

| 操作 | 按鍵 |
| --- | --- |
| 執行這格，游標移到下一格 | `Shift + Enter` |
| 執行這格，游標留在原地 | `Ctrl + Enter` |
| 在下方插入新格 | `Esc` 然後 `B` |
| 刪除這格 | `Esc` 然後 `D` `D`（按兩下 D） |
| 把這格改成文字說明（Markdown） | `Esc` 然後 `M` |

> ⚠️ **Jupyter 最大的坑：執行順序 ≠ 由上到下。**
> 你可以先跑第 5 格再跑第 2 格，變數會被覆蓋，結果就亂了。
> 每格左邊 `In [7]` 那個數字是「第幾個被執行的」，不是「第幾格」。
> **養成習慣：改完程式後,選單 `Run → Restart Kernel and Run All Cells`，確認從頭跑一次也是對的。**
> 這其實就是最原始的「回歸測試」——第 7 章會把它變成自動化的。

### ⚠️ Jupyter 找不到你的虛擬環境？

最常見症狀：在終端機 `pip install pandas` 裝好了，Notebook 裡 `import pandas` 卻說找不到。
原因是 Notebook 連到的 kernel 不是你的虛擬環境。診斷方式（在 Notebook 裡執行）：

```python
import sys
print(sys.executable)   # 這就是 Notebook 真正在用的 Python
```

解法是把虛擬環境註冊成一個 kernel：

```bash
python3 -m ipykernel install --user --name=drinkshop --display-name "Python (手搖飲教材)"
```

然後在 Notebook 右上角的 kernel 選單切換過去。

---

## 0.5 你的第一次「測試」

本教材從第一行程式就開始寫測試。這裡先讓你看看它長什麼樣——在 Jupyter 或互動模式輸入：

```python
import sys

assert sys.version_info >= (3, 10), f"版本太舊:{sys.version}"
print("環境檢查通過,版本是", sys.version.split()[0])
```

`assert` 的意思是：**「我斷言接下來這件事是真的，如果不是，立刻停下來告訴我。」**

- 條件成立 → 什麼都不會發生，程式繼續往下走（🟢 綠燈）
- 條件不成立 → 拋出 `AssertionError`，並顯示你寫的訊息（🔴 紅燈）

就這樣。這行不起眼的 `assert`，就是你整本書的測試主力。

試試故意讓它失敗，感受一下紅燈：

```python
assert 1 + 1 == 3, "數學壞掉了"
```

```
AssertionError: 數學壞掉了
```

> 🔍 **為什麼初學者該從 `assert` 開始，而不是直接學 pytest？**
> 因為 `assert` 沒有任何魔法：它是 Python 語法的一部分，不用安裝、不用設定、在任何地方都能用。
> 等你寫到幾十個測試、開始覺得「我想一次跑完所有測試並看到報表」的時候，
> 第 7 章自然會帶你升級到 `unittest` 和 `pytest`。**工具要在你感受到痛之後才學，才記得住。**

---

## 0.6 本章速記

```bash
# 診斷三連(任何環境問題都先跑這三行)
python3 --version                                   # 版本對嗎
python3 -c "import sys; print(sys.executable)"      # 用的是哪個 Python
pip list                                            # 裝了哪些套件

# 虛擬環境
python3 -m venv .venv        /  py -3 -m venv .venv
source .venv/bin/activate    /  .venv\Scripts\activate
deactivate

# Jupyter
jupyter lab
```

| 記住 | 為什麼 |
| --- | --- |
| 🪟 用 `py -3`，不要用 `python` | `python` 可能被商店捷徑劫持 |
| 🍎🐧 不要碰系統 Python | 會弄壞作業系統工具 |
| 一律用虛擬環境 | 專案之間互不干擾，刪掉就乾淨 |
| Jupyter 改完要 Restart & Run All | 避免執行順序造成的假象 |

---

## 🧪 練習

1. 在你的電腦上建立虛擬環境並啟動，然後執行 `python3 -c "import sys; print(sys.executable)"`，確認路徑裡有 `.venv`。
2. 打開 `notebooks/00-環境檢查.ipynb`，從頭執行到尾，確認全部通過。
3. 故意寫一個會失敗的 `assert`，看看錯誤訊息長什麼樣。（你會在接下來 14 章看它非常多次，早點習慣。）

---

➡️ 下一章：[第 1 章：第一支程式與變數](01-第一支程式與變數.md)
