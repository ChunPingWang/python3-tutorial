# %% [markdown]
# # 第 8 章：模組與套件 —— 把程式拆成好找的檔案
#
# > 🎬 **情境**
# > 你的 Notebook 已經有 87 格、400 多行。阿宏說「幫我改一下折扣」，你滑了三分鐘還沒找到那段程式。
# >
# > 更糟的是：員工小美也想用你的計價函式，但她只能**複製貼上**。
# > 下週你改了價格，她那份還是舊的。
#
# 這一章會**在你的硬碟上真的建立一個套件**，然後匯入它、測試它、最後清理掉。
# 全程使用 `pathlib`，Windows / macOS / Linux 結果完全一樣。

# %% [markdown]
# ## 8.1 😩 土法煉鋼：一個巨大的檔案
#
# | 問題 | 後果 |
# | --- | --- |
# | 找不到東西 | 每次改 code 都要先尋寶三分鐘 |
# | 無法重複使用 | 別人只能複製貼上，然後版本分岔 |
# | 無法分工 | 兩個人改同一個檔案 = git 衝突地獄 |
# | **測試很痛苦** | 要測一個函式，得先把整個 400 行跑一遍 |
#
# **Notebook 適合「學習和探索」，但不適合「累積成果」。**

# %% [markdown]
# ## 8.2 🧪 先寫測試：這次測試決定了檔案結構
#
# ```python
# from drinkshop.pricing import price_of      # ← 這一行就是設計
# ```
#
# 它同時宣告了三件事：
#
# 1. 會有一個叫 `drinkshop` 的**套件**（資料夾）
# 2. 裡面有一個叫 `pricing` 的**模組**（`pricing.py`）
# 3. 那個模組裡有一個叫 `price_of` 的函式
#
# > 🔍 **測試逼你先想清楚「東西該放哪裡」。**
# > 如果你寫出 `from utils import everything`，那是在告訴自己「我還沒想清楚」。

# %% [markdown]
# ## 8.3 動手：在硬碟上建立一個真的套件

# %%
from pathlib import Path

工作區 = Path("工作區") / "drinkshop-tools"
套件目錄 = 工作區 / "drinkshop"
測試目錄 = 工作區 / "tests"

套件目錄.mkdir(parents=True, exist_ok=True)     # parents=True：連中間的資料夾一起建
測試目錄.mkdir(parents=True, exist_ok=True)

print("建立於：", 工作區.resolve())

# %%
# menu.py —— 只放資料，改價格不用碰邏輯
(套件目錄 / "menu.py").write_text(
    '''"""菜單資料。"""

MENU = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
    "紅茶": {"中杯": 30, "大杯": 35},
}

SIZES = ("中杯", "大杯")
''',
    encoding="utf-8",
)

# pricing.py —— 只放邏輯，是純函式，超好測
(套件目錄 / "pricing.py").write_text(
    '''"""計價邏輯。"""

from decimal import Decimal, ROUND_HALF_UP

from drinkshop.menu import MENU

MEMBER_RATE = 0.9
MEMBER_THRESHOLD = 200


def round_half_up(value: float) -> int:
    """台灣習慣的四捨五入（逢五進一）。

    >>> round_half_up(58.5)
    59
    """
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def price_of(name: str, size: str, is_member: bool = False) -> int:
    """回傳指定品項、杯型的價格；會員自動套用折扣。"""
    price = MENU[name][size]
    if is_member:
        price = round_half_up(price * MEMBER_RATE)
    return price


if __name__ == "__main__":
    # 只有直接執行這個檔案時才會跑
    print("大杯珍奶：", price_of("珍珠奶茶", "大杯"))
''',
    encoding="utf-8",
)

# __init__.py —— 套件的「大門」，決定公開介面
(套件目錄 / "__init__.py").write_text(
    '''"""阿宏手搖飲營運工具。"""

from drinkshop.menu import MENU
from drinkshop.pricing import price_of, round_half_up

__all__ = ["MENU", "price_of", "round_half_up"]
''',
    encoding="utf-8",
)

for 檔案 in sorted(套件目錄.iterdir()):
    print("📄", 檔案.name, f"({檔案.stat().st_size} bytes)")

# %% [markdown]
# ## 8.4 ⚠️ 匯入路徑：`ModuleNotFoundError` 的根源
#
# 檔案建好了，但現在 `import drinkshop` 還是會失敗。**為什麼？**

# %%
try:
    import drinkshop
except ModuleNotFoundError as 錯誤:
    print("🔴 ModuleNotFoundError：", 錯誤)

# %% [markdown]
# ### Python 怎麼找模組？
#
# 按順序找 `sys.path` 裡的目錄：
#
# 1. 執行中的腳本所在的目錄（互動模式則是目前目錄）
# 2. `PYTHONPATH` 環境變數
# 3. 已安裝套件的目錄（`site-packages`）
#
# **關鍵：是「你執行 python 的位置」在決定，不是「檔案放在哪」。**

# %%
import sys

print("目前的 sys.path（前 4 個）：")
for p in sys.path[:4]:
    print("  ", p or "(目前目錄)")
print("\n我們的套件在：", 套件目錄.resolve().parent)
print("→ 不在 sys.path 裡，所以找不到。")

# %% [markdown]
# ### 三種正確解法
#
# **✅ 解法一：從專案根目錄執行（最簡單）**
#
# ```bash
# cd 專案根目錄
# python3 -m drinkshop.pricing      # 用 -m 執行模組（用點號、不加 .py）
# pytest                            # pytest 會自動處理
# ```
#
# ⚠️ 不是 `python3 drinkshop/pricing.py` —— 那會讓 Python 把 `drinkshop/` 當成根目錄，
# 於是 `from drinkshop.menu import MENU` 反而找不到。
#
# **✅ 解法二：`pyproject.toml` + 可編輯安裝（正式做法）**
#
# ```bash
# pip install -e .     # -e = editable，改程式碼立刻生效，不用重裝
# ```
#
# 裝完之後在**任何目錄**都能 `import drinkshop`。這是實務標準做法。
#
# **✅ 解法三：Notebook 裡的臨時做法**（下面示範）

# %%
專案根目錄 = 工作區.resolve()
if str(專案根目錄) not in sys.path:
    sys.path.insert(0, str(專案根目錄))

import drinkshop

print("🟢 成功匯入！", drinkshop.__doc__.strip())
print("大杯珍奶：", drinkshop.price_of("珍珠奶茶", "大杯"))
print("會員價  ：", drinkshop.price_of("珍珠奶茶", "大杯", is_member=True))

# %% [markdown]
# ⚠️ **解法三是權宜之計**，不要寫進正式程式。
#
# ⚠️⚠️ **絕對不要這樣做：**
#
# ```python
# sys.path.append("/Users/rex/workspace/專案")     # ✖ 寫死絕對路徑
# ```
#
# 換一台電腦、換一個作業系統就壞了。**寫死路徑是跨平台的頭號殺手。**
# 上面我們用的是 `工作區.resolve()` —— 從相對路徑算出來的，換到 Windows 一樣能跑。

# %% [markdown]
# ## 8.5 四種 import 寫法

# %%
import drinkshop.pricing                                   # 匯入整個模組
from drinkshop.pricing import price_of                     # 只匯入需要的
from drinkshop.pricing import price_of as 查價              # 取別名
from drinkshop import MENU                                 # 從 __init__.py 的公開介面

print(drinkshop.pricing.price_of("紅茶", "中杯"))
print(price_of("紅茶", "中杯"))
print(查價("紅茶", "中杯"))
print(list(MENU))

# %% [markdown]
# | 寫法 | 好處 | 壞處 |
# | --- | --- | --- |
# | `import pricing` | 看得出東西從哪來 | 每次要打全名 |
# | `from pricing import price_of` | 簡潔 | 多個模組同名函式時會混淆 |
# | `import pandas as pd` | 慣例別名 | — |
# | `from pricing import *` | — | ❌ **絕對不要用** |
#
# ⚠️ **為什麼 `import *` 是禁忌？** 你不知道它匯入了什麼，它可能默默覆蓋你已定義的東西，
# 而且讀程式的人看不出 `price_of` 是哪來的。

# %% [markdown]
# ### `__init__.py` 的封裝價值

# %%
print("使用者可以寫：from drinkshop import price_of")
print("不需要知道它其實住在 pricing.py 裡。")
print("\n公開介面：", drinkshop.__all__)
print("\n🔍 這叫「封裝」：你可以自由重構內部檔案結構，")
print("   只要 __init__.py 提供的介面不變，使用者的程式就不用改。")

# %% [markdown]
# ## 8.6 `if __name__ == "__main__":`
#
# Python 最常見、也最常被誤解的一行。

# %%
print("這個 notebook 的 __name__ 是：", __name__)
print("drinkshop.pricing 的 __name__ 是：", drinkshop.pricing.__name__)

# %% [markdown]
# | 情況 | `__name__` 的值 |
# | --- | --- |
# | 直接執行這個檔案（`python3 pricing.py`） | `"__main__"` |
# | 被別人 import | `"drinkshop.pricing"`（模組名） |
#
# 所以這行的意思是：**「只有當這個檔案被當成主程式直接執行時，才做底下的事。」**
#
# 注意剛才 `import drinkshop` 時，`pricing.py` 裡那行 `print("大杯珍奶：...")` **沒有被印出來** ——
# 因為它被 `if __name__ == "__main__":` 保護著。
#
# 沒有這行保護的話，別人每次 import 你的模組，你的測試輸出都會莫名其妙跑出來。

# %%
# 用 -m 直接執行模組，這時 __name__ 就是 "__main__"
import subprocess

結果 = subprocess.run(
    [sys.executable, "-m", "drinkshop.pricing"],
    cwd=專案根目錄,                       # 從專案根目錄執行 ← 解法一
    capture_output=True,
    text=True,
    encoding="utf-8",
)
print("$ python3 -m drinkshop.pricing")
print(結果.stdout or 結果.stderr)

# %% [markdown]
# ## 8.7 為模組寫測試

# %%
(測試目錄 / "test_pricing.py").write_text(
    '''"""pricing 模組的測試（pytest 與 unittest 都能跑）。"""

from drinkshop.pricing import price_of, round_half_up


def test_大杯珍奶是65元():
    assert price_of("珍珠奶茶", "大杯") == 65


def test_中杯珍奶是55元():
    assert price_of("珍珠奶茶", "中杯") == 55


def test_會員買大杯珍奶是59元():
    assert price_of("珍珠奶茶", "大杯", is_member=True) == 59


def test_不存在的品項會拋出KeyError():
    try:
        price_of("綠茶", "大杯")
    except KeyError:
        return
    raise AssertionError("應該要拋出 KeyError")


def test_台灣式四捨五入():
    assert round_half_up(58.5) == 59
    assert round_half_up(2.5) == 3
''',
    encoding="utf-8",
)
print("🟢 測試檔已建立")

# %%
# 用最陽春的方式跑這些測試（不需要 pytest）
import importlib

sys.path.insert(0, str(測試目錄))
測試模組 = importlib.import_module("test_pricing")

通過 = 失敗 = 0
for 名稱 in dir(測試模組):
    if 名稱.startswith("test_"):
        try:
            getattr(測試模組, 名稱)()
            print("🟢", 名稱)
            通過 += 1
        except AssertionError as 錯誤:
            print("🔴", 名稱, "：", 錯誤)
            失敗 += 1

print(f"\n共 {通過 + 失敗} 個測試，通過 {通過}，失敗 {失敗}")

# %% [markdown]
# 上面這 12 行，就是 pytest 在做的事情的最小版本：
# **找出名字以 `test_` 開頭的函式，一個一個呼叫，統計結果。**
#
# pytest 多做的事情是：漂亮的報表、assert 拆解、fixture、參數化、外掛生態系。
# 但核心概念就是這麼簡單。

# %%
# 如果裝了 pytest，就用真正的 pytest 跑一次
try:
    import pytest  # noqa: F401

    結果 = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "tests/"],
        cwd=專案根目錄,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print(結果.stdout[-2000:])
except ImportError:
    print("⚪ 沒有安裝 pytest。上面那個陽春版已經驗證過同樣的事情了。")
    print("   想試真正的 pytest：pip install pytest")

# %% [markdown]
# ## 8.8 ⚠️ Notebook 的自動重載
#
# 在 Notebook 裡 `import` 了自己的模組，然後你去改了那個 `.py` 檔 ——
# **Notebook 不會自動重新載入**，你會困惑「我明明改了為什麼沒效果」。

# %%
# 示範：改掉 menu.py 的價格
(套件目錄 / "menu.py").write_text(
    '''"""菜單資料。"""

MENU = {
    "珍珠奶茶": {"中杯": 60, "大杯": 70},
    "冬瓜檸檬": {"中杯": 45, "大杯": 50},
    "紅茶": {"中杯": 35, "大杯": 40},
}

SIZES = ("中杯", "大杯")
''',
    encoding="utf-8",
)

print("檔案已經改成大杯 70 了，但是：")
print("price_of('珍珠奶茶', '大杯') =", price_of("珍珠奶茶", "大杯"), "← 還是舊的！")

# %%
# 解法一：重新載入（最可靠的是重啟 kernel）
import drinkshop.menu
import drinkshop.pricing

importlib.reload(drinkshop.menu)
importlib.reload(drinkshop.pricing)

print("reload 之後：", drinkshop.pricing.price_of("珍珠奶茶", "大杯"))

# %% [markdown]
# **解法二：`autoreload`（開發時的黃金組合）**
#
# ```python
# %load_ext autoreload
# %autoreload 2
# ```
#
# 之後每次執行 cell 前，被修改過的模組都會自動重新載入。
# **這是「Notebook 探索 + .py 檔累積」這種工作流的必備設定。**

# %% [markdown]
# ## 8.9 拆檔原則
#
# ```
# drinkshop-tools/
# ├── pyproject.toml
# ├── drinkshop/
# │   ├── __init__.py       # 公開介面
# │   ├── menu.py           # 資料
# │   ├── pricing.py        # 邏輯（純函式）
# │   ├── orders.py         # 邏輯（純函式）
# │   ├── storage.py        # I/O：讀寫檔案
# │   └── report.py         # 報表
# └── tests/
#     ├── test_pricing.py
#     ├── test_orders.py
#     └── test_report.py
# ```
#
# | 原則 | 說明 |
# | --- | --- |
# | **按「職責」拆，不按「型別」拆** | `pricing.py`/`orders.py` ✔；`functions.py`/`classes.py` ✖ |
# | **資料和邏輯分開** | `menu.py` 只放資料，改價格不用碰邏輯 |
# | **I/O 集中在一兩個模組** | 其他模組保持純函式 → **好測試** |
# | **測試對應原始檔** | `pricing.py` ↔ `test_pricing.py` |
#
# > 🔍 **為什麼要把 I/O 集中？**
# > 讀寫檔案的函式很難測（要準備檔案、要清理、不同 OS 行為不同）。
# > 把它們關在 `storage.py`，其他 90% 的程式就都是純函式，三行測試就能驗證。
# >
# > 這個原則叫「**把副作用推到邊界**」，是 TDD 訓練出來的直覺。

# %% [markdown]
# ## 8.10 ⚠️ 不要和標準庫撞名

# %%
print("這些名字請不要拿來當你的檔案名：")
print("  random.py  json.py  email.py  test.py  string.py  csv.py  types.py")
print()
print("因為 import json 會匯入「你的檔案」而不是標準庫，")
print("而且錯誤訊息會非常詭異，通常要找很久。")

# %% [markdown]
# ### import 的順序慣例（PEP 8）
#
# ```python
# # 1. 標準庫
# import csv
# from pathlib import Path
#
# # 2. 第三方
# import pandas as pd
#
# # 3. 自己的
# from drinkshop.pricing import price_of
# ```

# %% [markdown]
# ## 8.11 清理

# %%
import shutil

# 把剛剛加進 sys.path 的東西移除，避免影響後續 notebook
for p in [str(專案根目錄), str(測試目錄)]:
    if p in sys.path:
        sys.path.remove(p)

for 名稱 in [m for m in list(sys.modules) if m.startswith(("drinkshop", "test_pricing"))]:
    del sys.modules[名稱]

shutil.rmtree(Path("工作區"))          # 整個資料夾刪掉（含子目錄）
print("🟢 清理完成，硬碟上不留東西")

# %% [markdown]
# ## 📌 本章速記
#
# ```python
# # 模組 = 一個 .py 檔；套件 = 一個含 __init__.py 的資料夾
# import pricing
# from pricing import price_of
# from pricing import price_of as 查價
# from pricing import *          # ❌ 絕對不要
#
# # 只在直接執行時跑
# if __name__ == "__main__":
#     main()
#
# # 找不到模組怎麼辦
# cd 專案根目錄 && python3 -m 套件.模組     # 用 -m
# pip install -e .                        # 正式做法
# sys.path.insert(0, str(專案根目錄))       # Notebook 權宜之計（別寫死路徑！）
#
# # Notebook 改了 .py 沒效果
# %load_ext autoreload
# %autoreload 2
#
# # import 順序：標準庫 / 第三方 / 自己的，各空一行
# # ⚠️ 不要把檔案取名 random.py、json.py、test.py…
# ```

# %% [markdown]
# ---
# ## 🧪 練習
#
# **練習 8-1：動手拆檔**
# 把第 1~7 章寫過的函式拆成 `mytools/pricing.py`、`mytools/stats.py`，
# 加上 `tests/`，在專案根目錄跑 `pytest`（或 `python3 -m unittest`）確認全綠。
#
# **練習 8-2：預測 `__name__`**
# ```python
# # a.py
# print("a 的 __name__ 是", __name__)
# # b.py
# import a
# print("b 的 __name__ 是", __name__)
# ```
# 執行 `python3 b.py` 會印出哪兩行？
#
# **練習 8-3：找出問題**
# 小美的專案裡有一個她自己寫的 `json.py`，而 `main.py` 裡有 `import json`。
# 會發生什麼？為什麼？怎麼修？

# %% [markdown]
# ---
# ➡️ 下一章：`09-檔案與路徑.ipynb` —— 關掉程式，今天的資料就全沒了。
