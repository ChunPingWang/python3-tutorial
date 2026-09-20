# 第 13 章：套件管理與 Jupyter 實務

> 🎬 **情境**
> 阿宏：「數字我看不懂，你畫成圖給我看。」
>
> 標準函式庫沒有畫圖工具。你需要 `matplotlib`。
> 你打開終端機 `pip install matplotlib`，裝好了，回到 Notebook `import matplotlib` ——
> **`ModuleNotFoundError`**。
>
> 你明明裝了。

---

## 13.1 😩 土法煉鋼：全部裝進系統 Python

新手最常見的做法是打開終端機就 `pip install`，然後遇到這四種災難：

| 災難 | 症狀 |
| --- | --- |
| **裝了卻找不到** | 裝進了 A 環境，Notebook 跑在 B 環境 |
| **版本衝突** | A 專案要 pandas 1.5、B 專案要 2.2，只能二選一 |
| **弄壞系統** | 🐧 `sudo pip install` 之後 `apt` 掛了 |
| **無法交接** | 同事問「要裝什麼？」你說不出來 |

---

## 13.2 💡 虛擬環境：一個專案一個房間

第 0 章提過，這裡講透。

```bash
# 建立(每個專案只做一次)
python3 -m venv .venv          # 🍎🐧
py -3 -m venv .venv            # 🪟

# 啟動(每次開新終端機都要)
source .venv/bin/activate      # 🍎🐧
.venv\Scripts\activate         # 🪟 PowerShell

# 確認
which python3                  # 🍎🐧 應該指向 .venv/bin/python3
where python                   # 🪟
python3 -c "import sys; print(sys.executable)"    # 最可靠,三平台通用

# 離開
deactivate
```

**虛擬環境其實只是一個資料夾。** 刪掉 `.venv` 就等於沒發生過，零風險。

⚠️ **`.venv` 絕對不要進 git**（裡面有上萬個檔案，而且綁定作業系統）。
`.gitignore` 要有 `.venv/`。

---

## 13.3 pip 與 requirements

```bash
pip install pandas                  # 安裝
pip install "pandas>=2.0,<3.0"      # 指定版本範圍
pip install -r requirements.txt     # 依照清單安裝
pip list                            # 看裝了什麼
pip show pandas                     # 看某個套件的詳情
pip uninstall pandas                # 移除
pip install -U pandas               # 升級
```

### 記錄依賴：兩個檔案的分工

```bash
pip freeze > requirements.txt       # 把目前環境完整凍結
```

⚠️ `pip freeze` 會把**所有**東西寫進去，包括「你裝的套件所依賴的套件」，
產出一份 80 行、你看不懂的清單。

**更好的做法是手寫 `requirements.txt`，只寫你「直接用到」的：**

```
# requirements.txt —— 我直接用到的東西
pandas>=2.0
matplotlib>=3.8
pytest>=8.0
```

| 檔案 | 內容 | 用途 |
| --- | --- | --- |
| `requirements.txt` | 手寫，只有直接依賴，寬鬆版本 | 給人看、給新環境裝 |
| `requirements.lock`（或 `pip freeze` 產物） | 自動產生，完整精確版本 | 重現一模一樣的環境 |

> 🔍 **版本怎麼指定？**
> - `pandas`（不指定）→ 今天裝 2.2，明年裝 3.0，**程式突然壞掉**
> - `pandas==2.2.0`（鎖死）→ 永遠不會壞，但也拿不到安全性修補
> - `pandas>=2.0,<3.0`（鎖大版本）→ ✔ **推薦**，大版本才會有破壞性變更

### ⚠️ 現代替代方案

| 工具 | 特色 |
| --- | --- |
| **uv** | 極快（Rust 寫的），可同時管理 Python 版本與套件，新專案推薦 |
| **Poetry** | 完整的專案管理與發布流程 |
| **conda** | 資料科學界常用，能裝非 Python 的相依（如 CUDA） |

本教材用 `venv` + `pip`，因為**它們內建、三平台一致、而且是所有其他工具的基礎**。

---

## 13.4 🔴 解決「明明裝了卻找不到」

這是本章開頭那個問題。**原因永遠是：pip 裝到 A 環境，Python 跑在 B 環境。**

### 診斷（在 Notebook 裡執行）

```python
import sys
print(sys.executable)        # Notebook 用的 Python
```

```bash
which pip                    # 🍎🐧  pip 屬於哪個 Python
where pip                    # 🪟
```

兩個路徑不一樣 → 找到原因了。

### ✅ 三個解法

**解法一（最可靠）：用 `sys.executable` 安裝**

在 Notebook 裡直接執行：

```python
import sys
!{sys.executable} -m pip install matplotlib
```

`{sys.executable}` 保證是「這個 Notebook 正在用的 Python」，**不可能裝錯**。

**解法二：把虛擬環境註冊成 kernel**

```bash
source .venv/bin/activate
pip install ipykernel
python3 -m ipykernel install --user --name=drinkshop --display-name "Python (手搖飲)"
```

然後在 Notebook 右上角切換 kernel。

**解法三：養成用 `python3 -m pip` 的習慣**

```bash
python3 -m pip install matplotlib        # ✔ 明確指定用哪個 python 的 pip
pip install matplotlib                   # ✖ 不確定是誰的 pip
```

> 🔍 **記住這個公式：`python -m pip` 裝的東西，`python` 一定找得到。**
> 這一行可以解決 90% 的「裝了卻找不到」。

---

## 13.5 Jupyter 實務技巧

### magic 指令

| 指令 | 用途 |
| --- | --- |
| `%time 運算式` | 測一次執行時間 |
| `%timeit 運算式` | 跑很多次取平均（比較準） |
| `%%time`（放在格子第一行） | 測整格的時間 |
| `%load_ext autoreload` + `%autoreload 2` | 自動重載修改過的模組 |
| `%who` / `%whos` | 列出目前定義的變數 |
| `%reset -f` | 清空所有變數 |
| `%pwd` | 目前工作目錄 |
| `!指令` | 執行 shell 指令 |
| `?函式` / `??函式` | 看說明 / 看原始碼 |

⚠️ **`!` 開頭的 shell 指令不跨平台**：`!ls` 在 Windows 上會失敗（要用 `!dir`）。
**教材與要分享的 Notebook，請一律改用 Python 寫法：**

```python
# ✖ 不跨平台
!ls 資料/

# ✔ 跨平台
from pathlib import Path
print(list(Path("資料").iterdir()))
```

### 讓 Notebook 可重現

⚠️ **Notebook 最大的問題：執行順序 ≠ 由上到下。**

`In [7]` 那個數字是「第幾個被執行的」，不是「第幾格」。
你可以先跑第 5 格再跑第 2 格，結果就亂了。

**三個習慣可以避免 90% 的痛苦：**

1. **交出去之前一定 `Restart Kernel and Run All Cells`**
   —— 這就是 Notebook 版的「回歸測試」
2. **不要在後面的格子修改前面格子的變數**
3. **把穩定的程式搬進 `.py` 檔**（第 8 章），Notebook 只留「呼叫 + 顯示」

### Notebook 與 git

`.ipynb` 是 JSON 檔，裡面塞滿了執行結果和 metadata，**git diff 幾乎無法閱讀**。

| 做法 | 說明 |
| --- | --- |
| commit 前清除輸出 | `jupyter nbconvert --clear-output --inplace *.ipynb` |
| 用 `nbstripout` | 自動在 commit 時清除輸出 |
| **用 jupytext** | 把 notebook 存成 `.py`，**git diff 變得可讀** |

> 🔍 **本教材就是用第三種做法**：
> `notebooks/src/*.py` 是可讀的原始碼（percent 格式），
> `tools/build_notebooks.py` 負責產生 `.ipynb`，而且會**實際執行每個 notebook 驗證**。
> 這樣既保有 Notebook 的互動性，又有 `.py` 的版本控制友善度。

---

## 13.6 畫圖給阿宏看：matplotlib

```python
import matplotlib.pyplot as plt

日期 = ["09/16", "09/17", "09/18", "09/19", "09/20"]
營收 = [3200, 2800, 4100, 5600, 6200]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(日期, 營收, marker="o")
ax.set_title("每日營收")
ax.set_xlabel("日期")
ax.set_ylabel("營收(元)")
ax.grid(axis="y", alpha=0.3)
plt.show()
```

### ⚠️ 中文字型：三平台的頭號問題

預設字型沒有中文，你會看到滿圖的豆腐方塊 `□□□`，還有一堆警告。

**跨平台解法：依系統挑字型**

```python
import platform
import matplotlib.pyplot as plt

系統 = platform.system()
候選字型 = {
    "Darwin":  ["PingFang HK", "Heiti TC", "Arial Unicode MS"],   # 🍎
    "Windows": ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"],  # 🪟
    "Linux":   ["Noto Sans CJK TC", "WenQuanYi Zen Hei"],         # 🐧
}[系統]

plt.rcParams["font.sans-serif"] = 候選字型
plt.rcParams["axes.unicode_minus"] = False      # 讓負號正常顯示
```

⚠️ 🐧 **Linux 通常要先裝字型**：

```bash
sudo apt install fonts-noto-cjk
```

⚠️ 裝完字型後要清 matplotlib 的字型快取，否則它還是找不到：

```python
import matplotlib
matplotlib.font_manager._load_fontmanager(try_read_cache=False)
```

> 💡 **更省事的做法：圖表標題和座標軸用英文。**
> 這聽起來是逃避，但在需要跨平台、跨機器、進 CI 的專案裡，
> 這是最務實的選擇。中文留給給人看的報表文字。

---

## 13.7 pandas：表格資料的瑞士刀

```python
import pandas as pd

df = pd.read_csv("訂單.csv", encoding="utf-8")

df.head()                       # 前 5 筆
df.info()                       # 欄位與型別
df.describe()                   # 統計摘要
df["金額"].sum()                # 加總
df.groupby("品項")["金額"].sum()  # 分組加總 ← 最常用
df.sort_values("金額", ascending=False).head(3)     # 前三名
df.to_csv("輸出.csv", index=False, encoding="utf-8-sig")   # 給 Excel 看
```

> 🔍 **什麼時候該用 pandas，什麼時候用標準庫？**
>
> | 情況 | 用什麼 |
> | --- | --- |
> | 幾百筆、邏輯簡單 | `csv` + `dict` 就好，**少一個依賴** |
> | 幾萬筆以上 | pandas（快非常多） |
> | 要做樞紐分析、合併多個表 | pandas |
> | 要寫成獨立小工具給人用 | 標準庫（不用叫對方裝東西） |
>
> **不要因為「大家都用 pandas」就用。** 多一個依賴就多一份維護成本。
> 第 14 章的專案刻意只用標準庫，你會發現它完全夠用。

⚠️ **pandas 的坑**：`df["金額"]` 讀進來可能是 `object`（字串）而不是數字。
`df.info()` 每次都要看一眼。

---

## 13.8 🧪 測試與依賴

### 選配依賴的正確處理方式

```python
try:
    import matplotlib.pyplot as plt
    有繪圖 = True
except ImportError:
    有繪圖 = False

def 產生報表(資料, 畫圖=False):
    文字報表 = 格式化(資料)              # 核心功能,不依賴任何第三方套件
    if 畫圖 and 有繪圖:
        繪圖(資料)
    return 文字報表
```

**核心功能不依賴選配套件**，這樣：

- 沒裝 matplotlib 的人照樣能用
- 測試不需要裝 matplotlib
- CI 跑得更快

### pytest 的跳過機制

```python
import pytest

matplotlib = pytest.importorskip("matplotlib")    # 沒裝就跳過這個測試

@pytest.mark.skipif(sys.platform == "win32", reason="Windows 沒有這個字型")
def test_中文字型(): ...
```

### 在 CI 裡跑測試（跨平台驗證）

```yaml
# .github/workflows/test.yml
name: test
on: [push, pull_request]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest -v
```

> 🔍 **這就是「真正的跨平台驗證」。**
> 你在 Mac 上寫的程式，CI 會同時在 Windows 和 Linux 上跑一遍。
> 第 9 章那些編碼、路徑、換行的坑，CI 會在你上線前抓出來。
>
> **而這一切的前提是：你有測試。** 沒有測試，CI 什麼也驗證不了。

---

## 13.9 📌 本章速記

```bash
# 虛擬環境
python3 -m venv .venv / py -3 -m venv .venv
source .venv/bin/activate / .venv\Scripts\activate
deactivate
# ⚠️ .venv 不要進 git

# pip
python3 -m pip install 套件      # ✔ 用 -m,保證裝對地方
pip install -r requirements.txt
pip list / pip show / pip install -U

# requirements.txt 手寫,只寫直接依賴,鎖大版本
pandas>=2.0,<3.0
```

```python
# Notebook 裡安裝(保證裝對)
import sys
!{sys.executable} -m pip install matplotlib

# magic
%timeit 運算式
%load_ext autoreload
%autoreload 2
%who
# ⚠️ !ls 不跨平台,改用 pathlib

# 可重現三習慣
# 1. 交出去前 Restart & Run All
# 2. 不在後面的格子改前面的變數
# 3. 穩定的程式搬進 .py

# matplotlib 中文
plt.rcParams["font.sans-serif"] = ["PingFang HK"]   # 依系統挑
plt.rcParams["axes.unicode_minus"] = False
# 💡 更省事:圖表用英文標題

# 選配依賴
try: import matplotlib
except ImportError: 有繪圖 = False
pytest.importorskip("matplotlib")
```

---

## 🧪 練習

1. 建立一個乾淨的虛擬環境，裝好 `requirements.txt`，用 `sys.executable` 確認 Notebook 用的是它。
2. 把 `requirements.txt` 的 `pandas` 改成 `pandas>=2.0,<3.0`，說明為什麼這比 `pandas` 和 `pandas==2.2.0` 都好。
3. 寫一個 `產生圖表(資料, 輸出路徑)`，要求：沒裝 matplotlib 時**不要崩潰**，而是回傳 `False` 並記錄警告。為它寫兩個測試（有裝 / 沒裝，用 `unittest.mock.patch` 模擬沒裝的情況）。
4. 在你的專案加一個 GitHub Actions 設定，讓測試同時在 Windows、macOS、Linux 上跑。

---

📓 **對應 Notebook**：[`notebooks/13-套件管理與-Jupyter-實務.ipynb`](../notebooks/13-套件管理與-Jupyter-實務.ipynb)

➡️ 下一章：[第 14 章：綜合專案](14-綜合專案.md) —— 用 TDD 從零做完整個營運儀表板。
