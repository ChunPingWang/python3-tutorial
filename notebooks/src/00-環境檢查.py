# %% [markdown]
# # 第 0 章：環境檢查
#
# 這本 Notebook 不教語法，只做一件事：**確認你的環境是好的**。
#
# 請由上往下，每一格按 `Shift + Enter` 執行。全部看到 🟢 就可以安心進第 1 章。

# %% [markdown]
# ## 1. 我現在用的是哪一個 Python？
#
# 這是所有環境問題的萬用診斷。如果之後出現「明明裝了卻說找不到」，第一件事就是回來跑這格。

# %%
import sys
import platform

print("版本    :", sys.version.split()[0])
print("執行檔  :", sys.executable)
print("作業系統:", platform.system(), platform.release())

# %% [markdown]
# **怎麼看這三行？**
#
# - **版本**：需要 3.10 以上。
# - **執行檔**：路徑裡有 `.venv` 代表你在虛擬環境裡（推薦）。若是 `/usr/bin/python3` 或系統路徑，代表虛擬環境沒啟動成功。
# - **作業系統**：`Darwin` 是 macOS、`Windows` 是 Windows、`Linux` 是 Linux。
#
# 本教材所有程式碼在這三個系統上結果都一樣，你不需要因為系統不同改任何東西。

# %% [markdown]
# ## 2. 第一個測試：版本夠不夠新
#
# `assert` 的意思是「我斷言這件事是真的，如果不是，立刻停下來」。
#
# - 條件成立 → 什麼都不會發生，程式繼續（🟢 綠燈）
# - 條件不成立 → 拋出 `AssertionError`（🔴 紅燈）

# %%
assert sys.version_info >= (3, 10), f"版本太舊：{sys.version}，請升級到 3.10 以上"
print("🟢 版本檢查通過")

# %% [markdown]
# ## 3. 感受一下紅燈
#
# 測試會失敗才有價值。下面這格故意寫一個錯的斷言，讓你看看紅燈長什麼樣。
#
# （這裡用 `try / except` 把錯誤接住，好讓 Notebook 能一路跑完；
# 平常你自己寫的時候不用這樣包，讓它直接噴錯就好。）

# %%
try:
    assert 1 + 1 == 3, "數學壞掉了"
except AssertionError as 錯誤:
    print("🔴 紅燈！錯誤型別：AssertionError")
    print("   訊息：", 錯誤)

# %% [markdown]
# 看懂這個畫面很重要。接下來 14 章，你會靠它知道自己寫對了沒有。

# %% [markdown]
# ## 4. 中文顯示正常嗎？
#
# 這一格在 Windows 舊版終端機上偶爾會出問題。在 Jupyter 裡幾乎不會，跑一下確認。

# %%
訊息 = "阿宏手搖飲：珍珠奶茶 65 元 🧋"
print(訊息)

# Python 3 的字串是以「字元」為單位計算的，一個中文字算 1，一個 emoji 也算 1
assert 訊息.startswith("阿宏"), "中文字串處理異常"
assert len("珍珠奶茶") == 4, "中文字元計數異常"
assert len("🧋") == 1, "emoji 計數異常"
print("🟢 中文與 emoji 正常，整句長度：", len(訊息), "個字元")

# %% [markdown]
# ## 5. 檔案讀寫與路徑（跨平台）
#
# 第 9 章會詳細講。這裡先確認你的環境能正常建立檔案，
# 並且示範**本教材處理路徑的標準做法**：一律用 `pathlib`，絕不自己拼 `/` 或 `\`。

# %%
from pathlib import Path

工作區 = Path("工作區")
工作區.mkdir(exist_ok=True)          # 已存在也不報錯

測試檔 = 工作區 / "環境檢查.txt"      # 用 / 組路徑，Windows 上會自動變成 \
測試檔.write_text("測試成功", encoding="utf-8")

內容 = 測試檔.read_text(encoding="utf-8")
assert 內容 == "測試成功"

print("🟢 檔案讀寫正常")
print("   檔案位置：", 測試檔.resolve())

# %% [markdown]
# ⚠️ 注意 `encoding="utf-8"`。
# **Windows 的預設編碼不是 UTF-8**，不寫這個參數，中文檔案在 Windows 上讀出來會變亂碼或直接報錯。
# 本教材每一次讀寫文字檔都會寫它，請養成習慣。

# %% [markdown]
# ## 6. 清理
#
# 把剛剛產生的測試檔刪掉，不留垃圾。

# %%
測試檔.unlink()                       # 刪檔案
工作區.rmdir()                        # 刪空資料夾
print("🟢 清理完成")

# %% [markdown]
# ## 7. 選配套件檢查
#
# 第 1~12 章**完全不需要**任何第三方套件。
# 下面只是告訴你第 13、14 章要用的東西裝了沒，紅字不影響你現在學習。

# %%
for 套件名 in ["pytest", "pandas", "matplotlib"]:
    try:
        __import__(套件名)
        print(f"🟢 {套件名:<12} 已安裝")
    except ImportError:
        print(f"⚪ {套件名:<12} 未安裝（第 13 章之前用不到）")

# %% [markdown]
# ## ✅ 全部綠燈？
#
# 那就可以開始了 → `01-第一支程式與變數.ipynb`
#
# 如果卡住了，請看 [附錄 C：疑難排解](../docs/附錄C-疑難排解.md)。
