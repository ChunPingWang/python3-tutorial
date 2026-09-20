# %% [markdown]
# # 第 13 章：套件管理與 Jupyter 實務
#
# > 🎬 **情境**
# > 阿宏：「數字我看不懂，你畫成圖給我看。」
# >
# > 標準函式庫沒有畫圖工具，你需要 `matplotlib`。
# > 你在終端機 `pip install matplotlib`，裝好了，回到 Notebook `import matplotlib` ——
# > **`ModuleNotFoundError`**。你明明裝了。

# %% [markdown]
# ## 13.1 😩 土法煉鋼：全部裝進系統 Python
#
# | 災難 | 症狀 |
# | --- | --- |
# | **裝了卻找不到** | 裝進 A 環境，Notebook 跑在 B 環境 |
# | **版本衝突** | A 專案要 pandas 1.5、B 專案要 2.2，只能二選一 |
# | **弄壞系統** | 🐧 `sudo pip install` 之後 `apt` 掛了 |
# | **無法交接** | 同事問「要裝什麼？」你說不出來 |

# %% [markdown]
# ## 13.2 🔴 診斷：我現在到底在哪個環境？
#
# 這三行可以解決 90% 的環境問題。**出事時先跑它們。**

# %%
import platform
import sys
from pathlib import Path

print("Python 版本  :", sys.version.split()[0])
print("執行檔路徑   :", sys.executable)
print("作業系統     :", platform.system())
print("在虛擬環境嗎 :", "是" if sys.prefix != sys.base_prefix else "否（用的是系統 Python）")
print("套件搜尋路徑 :")
for p in sys.path[:5]:
    print("   ", p or "(目前目錄)")

# %% [markdown]
# **怎麼看：**
#
# - **執行檔路徑**裡有 `.venv` → 你在虛擬環境裡（推薦）
# - **在虛擬環境嗎** → `sys.prefix != sys.base_prefix` 是最可靠的判斷方式

# %% [markdown]
# ## 13.3 💡 虛擬環境：一個專案一個房間
#
# ```bash
# # 建立（每個專案只做一次）
# python3 -m venv .venv          # 🍎🐧
# py -3 -m venv .venv            # 🪟
#
# # 啟動（每次開新終端機都要）
# source .venv/bin/activate      # 🍎🐧
# .venv\Scripts\activate         # 🪟 PowerShell
#
# # 離開
# deactivate
# ```
#
# **虛擬環境其實只是一個資料夾。** 刪掉 `.venv` 就等於沒發生過，零風險。
#
# ⚠️ **`.venv` 絕對不要進 git**（上萬個檔案，而且綁定作業系統）。

# %%
# 看看這個環境裝了什麼（前 15 個）
import subprocess

結果 = subprocess.run(
    [sys.executable, "-m", "pip", "list", "--format=freeze"],
    capture_output=True, text=True, encoding="utf-8",
)
套件們 = 結果.stdout.strip().splitlines()
print(f"共 {len(套件們)} 個套件，前 15 個：")
for 行 in 套件們[:15]:
    print("  ", 行)

# %% [markdown]
# ## 13.4 ✅ 解決「明明裝了卻找不到」
#
# **原因永遠是：pip 裝到 A 環境，Python 跑在 B 環境。**
#
# ### 解法一（最可靠）：在 Notebook 裡用 `sys.executable` 安裝
#
# ```python
# import sys
# !{sys.executable} -m pip install matplotlib
# ```
#
# `{sys.executable}` 保證是「這個 Notebook 正在用的 Python」，**不可能裝錯**。
#
# ### 解法二：把虛擬環境註冊成 kernel
#
# ```bash
# source .venv/bin/activate
# pip install ipykernel
# python3 -m ipykernel install --user --name=drinkshop --display-name "Python (手搖飲)"
# ```
#
# ### 解法三：養成用 `python3 -m pip` 的習慣
#
# ```bash
# python3 -m pip install matplotlib     # ✔ 明確指定用哪個 python 的 pip
# pip install matplotlib                # ✖ 不確定是誰的 pip
# ```
#
# > 🔍 **記住這個公式：`python -m pip` 裝的東西，`python` 一定找得到。**

# %% [markdown]
# ## 13.5 requirements.txt：記錄依賴

# %%
# pip freeze 會把「所有」東西寫進去，包括依賴的依賴
print("pip freeze 產出的行數：", len(套件們), "行 ← 你看不懂其中大部分")
print()
print("更好的做法是手寫 requirements.txt，只寫你「直接用到」的：")
print("""
# requirements.txt
pandas>=2.0,<3.0
matplotlib>=3.8
pytest>=8.0
""")

# %% [markdown]
# | 檔案 | 內容 | 用途 |
# | --- | --- | --- |
# | `requirements.txt` | 手寫，只有直接依賴，寬鬆版本 | 給人看、給新環境裝 |
# | `pip freeze` 的產物 | 自動產生，完整精確版本 | 重現一模一樣的環境 |
#
# > 🔍 **版本怎麼指定？**
# >
# > - `pandas`（不指定）→ 今天裝 2.2，明年裝 3.0，**程式突然壞掉**
# > - `pandas==2.2.0`（鎖死）→ 永遠不會壞，但也拿不到安全性修補
# > - `pandas>=2.0,<3.0`（鎖大版本）→ ✔ **推薦**，大版本才會有破壞性變更

# %% [markdown]
# ### ⚠️ 現代替代方案
#
# | 工具 | 特色 |
# | --- | --- |
# | **uv** | 極快（Rust 寫的），可同時管理 Python 版本與套件，新專案推薦 |
# | **Poetry** | 完整的專案管理與發布流程 |
# | **conda** | 資料科學界常用，能裝非 Python 的相依（如 CUDA） |
#
# 本教材用 `venv` + `pip`，因為**它們內建、三平台一致、而且是所有其他工具的基礎**。

# %% [markdown]
# ## 13.6 Jupyter magic 指令

# %%
# %timeit：跑很多次取平均（這是 Jupyter 的 magic，不是 Python 語法）
資料 = list(range(10000))
%timeit sum(資料)

# %%
# %time：測一次
%time _ = sum(資料)

# %% [markdown]
# | 指令 | 用途 |
# | --- | --- |
# | `%time 運算式` | 測一次執行時間 |
# | `%timeit 運算式` | 跑很多次取平均（比較準） |
# | `%%time`（格子第一行） | 測整格的時間 |
# | `%load_ext autoreload` + `%autoreload 2` | 自動重載修改過的模組 |
# | `%who` / `%whos` | 列出目前定義的變數 |
# | `%reset -f` | 清空所有變數 |
# | `!指令` | 執行 shell 指令 |
# | `?函式` / `??函式` | 看說明 / 看原始碼 |

# %% [markdown]
# ### ⚠️ `!` 開頭的 shell 指令不跨平台

# %%
# ✖ 不跨平台：!ls 在 Windows 上會失敗（要用 !dir）
# !ls

# ✔ 跨平台：用 Python 寫
print("目前目錄下的項目：")
for 項目 in sorted(Path(".").iterdir())[:8]:
    標記 = "📁" if 項目.is_dir() else "📄"
    print("  ", 標記, 項目.name)

# %% [markdown]
# **教材與要分享的 Notebook，請一律改用 Python 寫法。**

# %% [markdown]
# ## 13.7 ⚠️ 讓 Notebook 可重現
#
# **Notebook 最大的問題：執行順序 ≠ 由上到下。**
#
# `In [7]` 那個數字是「第幾個被執行的」，不是「第幾格」。
# 你可以先跑第 5 格再跑第 2 格，結果就亂了。

# %%
# 示範這個陷阱有多容易發生
營收 = 1000
print("第一次執行：營收 =", 營收)

營收 = 營收 * 2          # 如果你重複執行這一格三次…
print("重複執行後：營收 =", 營收, "← 每跑一次就翻倍，但程式碼看起來沒變")

# %% [markdown]
# **三個習慣可以避免 90% 的痛苦：**
#
# 1. **交出去之前一定 `Restart Kernel and Run All Cells`**
#    —— 這就是 Notebook 版的「回歸測試」
# 2. **不要在後面的格子修改前面格子的變數**
# 3. **把穩定的程式搬進 `.py` 檔**（第 8 章），Notebook 只留「呼叫 + 顯示」

# %% [markdown]
# ### Notebook 與 git
#
# `.ipynb` 是 JSON 檔，塞滿執行結果和 metadata，**git diff 幾乎無法閱讀**。
#
# | 做法 | 說明 |
# | --- | --- |
# | commit 前清除輸出 | `jupyter nbconvert --clear-output --inplace *.ipynb` |
# | 用 `nbstripout` | 自動在 commit 時清除輸出 |
# | **用 jupytext** | 把 notebook 存成 `.py`，**git diff 變得可讀** |
#
# > 🔍 **本教材就是用第三種做法**：
# > `notebooks/src/*.py` 是可讀的原始碼（percent 格式），
# > `tools/build_notebooks.py` 產生 `.ipynb`，而且會**實際執行每個 notebook 驗證**。
# > 既保有 Notebook 的互動性，又有 `.py` 的版本控制友善度。

# %% [markdown]
# ## 13.8 畫圖給阿宏看：matplotlib

# %%
日期 = ["09/16", "09/17", "09/18", "09/19", "09/20"]
營收資料 = [3200, 2800, 4100, 5600, 6200]

try:
    import matplotlib

    matplotlib.use("Agg")                    # 不開視窗，適合自動化環境
    import matplotlib.pyplot as plt

    有繪圖 = True
    print("🟢 matplotlib", matplotlib.__version__, "可用")
except ImportError:
    有繪圖 = False
    print("⚪ 沒裝 matplotlib。這章的核心觀念不需要它 ——")
    print("   要裝的話：!{sys.executable} -m pip install matplotlib")

# %%
# ⚠️ 中文字型：三平台的頭號問題
# 預設字型沒有中文，你會看到滿圖的豆腐方塊 □□□

候選字型 = {
    "Darwin": ["PingFang HK", "Heiti TC", "Arial Unicode MS"],          # 🍎
    "Windows": ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"],     # 🪟
    "Linux": ["Noto Sans CJK TC", "WenQuanYi Zen Hei"],                 # 🐧
}.get(platform.system(), [])

print("你的系統建議字型：", 候選字型)
print()
print("設定方式：")
print('  plt.rcParams["font.sans-serif"] = 候選字型')
print('  plt.rcParams["axes.unicode_minus"] = False   # 讓負號正常顯示')
print()
print("🐧 Linux 通常要先裝字型：sudo apt install fonts-noto-cjk")
print()
print("💡 更省事的做法：圖表標題和座標軸用英文。")
print("   在需要跨平台、進 CI 的專案裡，這是最務實的選擇。")

# %%
if 有繪圖:
    plt.rcParams["font.sans-serif"] = 候選字型 or plt.rcParams["font.sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(日期, 營收資料, marker="o")
    ax.set_title("Daily Revenue")            # 用英文，跨平台不會變豆腐
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue (NTD)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    plt.show()
else:
    # 沒有 matplotlib 也能畫圖 —— 用文字長條圖
    最大值 = max(營收資料)
    print("每日營收（文字版長條圖）")
    print("-" * 40)
    for d, v in zip(日期, 營收資料):
        長度 = round(v / 最大值 * 25)
        print(f"{d}  {'█' * 長度} {v:,}")

# %%
# 不管有沒有 matplotlib，這個純文字版本永遠能用（而且好測試）
def 文字長條圖(標籤們, 數值們, 寬度=25) -> str:
    """產生純文字的長條圖，不需要任何第三方套件。

    >>> print(文字長條圖(["a", "b"], [1, 2], 寬度=2))
    a  █ 1
    b  ██ 2
    """
    最大值 = max(數值們) or 1
    return "\n".join(
        f"{標籤}  {'█' * round(值 / 最大值 * 寬度)} {值:,}"
        for 標籤, 值 in zip(標籤們, 數值們)
    )


print(文字長條圖(日期, 營收資料))

import doctest

執行器 = doctest.DocTestRunner()
for 測試 in doctest.DocTestFinder().find(文字長條圖):
    執行器.run(測試)
統計 = 執行器.summarize(verbose=False)
print(f"\n🟢 doctest：{統計.attempted} 個，失敗 {統計.failed} 個")

# %% [markdown]
# ## 13.9 pandas：表格資料的瑞士刀
#
# ```python
# import pandas as pd
#
# df = pd.read_csv("訂單.csv", encoding="utf-8")
# df.head()                          # 前 5 筆
# df.info()                          # 欄位與型別 ← 每次都要看一眼
# df["金額"].sum()
# df.groupby("品項")["金額"].sum()     # 分組加總 ← 最常用
# df.sort_values("金額", ascending=False).head(3)
# df.to_csv("輸出.csv", index=False, encoding="utf-8-sig")   # 給 Excel 看
# ```
#
# > 🔍 **什麼時候該用 pandas，什麼時候用標準庫？**
# >
# > | 情況 | 用什麼 |
# > | --- | --- |
# > | 幾百筆、邏輯簡單 | `csv` + `dict` 就好，**少一個依賴** |
# > | 幾萬筆以上 | pandas（快非常多） |
# > | 要做樞紐分析、合併多個表 | pandas |
# > | 要寫成獨立小工具給人用 | 標準庫（不用叫對方裝東西） |
# >
# > **不要因為「大家都用 pandas」就用。** 多一個依賴就多一份維護成本。
# > 第 14 章的專案刻意只用標準庫，你會發現它完全夠用。

# %%
try:
    import pandas as pd

    df = pd.DataFrame({"品項": ["珍奶", "紅茶", "珍奶"], "金額": [65, 35, 55]})
    print(df)
    print("\n分組加總：")
    print(df.groupby("品項")["金額"].sum())
except ImportError:
    print("⚪ 沒裝 pandas。用標準庫做同一件事：")
    from collections import defaultdict

    資料 = [("珍奶", 65), ("紅茶", 35), ("珍奶", 55)]
    合計 = defaultdict(int)
    for 品項, 金額 in 資料:
        合計[品項] += 金額
    print("  ", dict(合計), "← 四行，沒有任何依賴")

# %% [markdown]
# ## 13.10 🧪 測試與依賴

# %% [markdown]
# ### 選配依賴的正確處理方式
#
# **核心功能不依賴選配套件**，這樣：沒裝的人照樣能用、測試不用裝、CI 跑得更快。

# %%
def 產生報表(標籤們, 數值們, 畫圖=False, 輸出路徑=None) -> str:
    """核心功能（文字報表）不依賴任何第三方套件；畫圖是選配。"""
    報表 = 文字長條圖(標籤們, 數值們)

    if 畫圖:
        if not 有繪圖:
            print("⚠️ 未安裝 matplotlib，跳過繪圖（核心報表不受影響）")
        else:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(標籤們, 數值們)
            ax.set_title("Revenue")
            if 輸出路徑:
                fig.savefig(輸出路徑, dpi=100, bbox_inches="tight")
            plt.close(fig)

    return 報表


# 核心功能的測試：不需要 matplotlib，毫秒完成
def test_報表不依賴繪圖套件():
    報表 = 產生報表(["a", "b"], [1, 2])
    assert "a" in 報表 and "b" in 報表
    assert "1" in 報表


test_報表不依賴繪圖套件()
print("🟢 核心功能測試通過（完全不碰 matplotlib）")

# %%
# 繪圖功能的測試：用 tempfile，跨平台、不留垃圾
import tempfile

if 有繪圖:
    with tempfile.TemporaryDirectory() as 暫存:
        圖檔 = Path(暫存) / "報表.png"
        產生報表(日期, 營收資料, 畫圖=True, 輸出路徑=圖檔)
        assert 圖檔.exists() and 圖檔.stat().st_size > 0
        print(f"🟢 圖檔產生成功（{圖檔.stat().st_size:,} bytes），離開 with 後自動刪除")
else:
    print("⚪ 跳過繪圖測試（pytest 的寫法是 pytest.importorskip('matplotlib')）")

# %% [markdown]
# ### pytest 的跳過機制
#
# ```python
# matplotlib = pytest.importorskip("matplotlib")      # 沒裝就跳過這個測試
#
# @pytest.mark.skipif(sys.platform == "win32", reason="Windows 沒有這個字型")
# def test_中文字型(): ...
# ```

# %% [markdown]
# ## 13.11 在 CI 裡跑測試（真正的跨平台驗證）
#
# ```yaml
# # .github/workflows/test.yml
# name: test
# on: [push, pull_request]
# jobs:
#   test:
#     runs-on: ${{ matrix.os }}
#     strategy:
#       matrix:
#         os: [ubuntu-latest, macos-latest, windows-latest]
#         python-version: ["3.10", "3.12"]
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#         with:
#           python-version: ${{ matrix.python-version }}
#       - run: pip install -e ".[dev]"
#       - run: pytest -v
# ```
#
# > 🔍 **這就是「真正的跨平台驗證」。**
# > 你在 Mac 上寫的程式，CI 會同時在 Windows 和 Linux 上跑一遍。
# > 第 9 章那些編碼、路徑、換行的坑，CI 會在你上線前抓出來。
# >
# > **而這一切的前提是：你有測試。** 沒有測試，CI 什麼也驗證不了。

# %% [markdown]
# ## 📌 本章速記
#
# ```bash
# python3 -m venv .venv / py -3 -m venv .venv
# source .venv/bin/activate / .venv\Scripts\activate
# python3 -m pip install 套件          # ✔ 用 -m，保證裝對地方
# # ⚠️ .venv 不要進 git
# ```
#
# ```python
# # 診斷三行
# sys.executable / sys.prefix != sys.base_prefix / sys.path
#
# # Notebook 裡安裝（保證裝對）
# !{sys.executable} -m pip install matplotlib
#
# # magic：%timeit %time %who %load_ext autoreload
# # ⚠️ !ls 不跨平台，改用 pathlib
#
# # 可重現三習慣：Restart & Run All、不回頭改變數、穩定程式搬進 .py
#
# # matplotlib 中文：依系統挑字型；💡 更省事 —— 圖表用英文
#
# # 選配依賴
# try: import matplotlib
# except ImportError: 有繪圖 = False
# pytest.importorskip("matplotlib")
# ```

# %% [markdown]
# ---
# ## 🧪 練習
#
# 1. 建立一個乾淨的虛擬環境，裝好 `requirements.txt`，用 `sys.executable` 確認 Notebook 用的是它。
# 2. 把 `requirements.txt` 的 `pandas` 改成 `pandas>=2.0,<3.0`，
#    說明為什麼這比 `pandas` 和 `pandas==2.2.0` 都好。
# 3. 寫一個 `產生圖表(資料, 輸出路徑)`：沒裝 matplotlib 時**不要崩潰**，而是回傳 `False` 並記錄警告。
#    為它寫兩個測試（有裝 / 沒裝，用 `unittest.mock.patch` 模擬沒裝的情況）。
# 4. 在你的專案加一個 GitHub Actions 設定，讓測試同時在 Windows、macOS、Linux 上跑。

# %% [markdown]
# ---
# ➡️ 下一章：`14-綜合專案.ipynb` —— 用 TDD 從零做完整個營運儀表板。
