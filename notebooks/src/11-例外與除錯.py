# %% [markdown]
# # 第 11 章：例外與除錯 —— 當事情出錯的時候
#
# > 🎬 **情境**
# > 上線第一天。客人在自助點餐機的數量欄輸入「兩杯」。
# >
# > ```
# > ValueError: invalid literal for int() with base 10: '兩杯'
# > ```
# >
# > 整台點餐機掛掉，後面排了八個客人。阿宏在電話那頭很冷靜地問：「所以現在怎麼辦？」

# %%
MENU = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
}

# 重現災難現場
try:
    數量 = int("兩杯")
except ValueError as 錯誤:
    print("🔴 ValueError：", 錯誤)

# %% [markdown]
# ## 11.1 😩 土法煉鋼：用 if 檢查所有可能
#
# ```python
# if 輸入.isdigit():
#     數量 = int(輸入)
# else:
#     數量 = 1
#
# if 品項 in MENU:
#     if 杯型 in MENU[品項]:
#         價格 = MENU[品項][杯型]
#     else:
#         價格 = 0          # ← 最可怕的一行
# ```
#
# 1. **檢查不完**。檔案在你 `exists()` 之後、`read_text()` 之前被刪掉呢？
# 2. **主要邏輯被淹沒**。10 行程式裡 8 行在檢查。
# 3. **默默給錯答案**。`價格 = 0` 比直接爆炸更可怕 —— 阿宏賠錢賠三個月才發現。

# %% [markdown]
# ## 11.2 例外的哲學：EAFP
#
# > **EAFP — Easier to Ask Forgiveness than Permission**
# > 先做再說、出事再處理，比事前檢查每個條件容易。

# %%
# LBYL：先檢查再跳
if "珍珠奶茶" in MENU and "大杯" in MENU["珍珠奶茶"]:
    價格 = MENU["珍珠奶茶"]["大杯"]
else:
    價格 = None
print("LBYL：", 價格)

# EAFP：先做，出事再說 ← Python 風格
try:
    價格 = MENU["珍珠奶茶"]["大杯"]
except KeyError:
    價格 = None
print("EAFP：", 價格)

# %% [markdown]
# EAFP 的好處：**主要邏輯是乾淨的一行，錯誤處理集中在一個地方。**

# %% [markdown]
# ## 11.3 💡 try / except

# %%
def 解析數量_第一版(輸入值):
    try:
        return int(輸入值)
    except ValueError:
        print("   （請輸入數字）")
        return 1


for 測試值 in ["2", "兩杯", "3"]:
    print(f"輸入 {測試值!r} → {解析數量_第一版(測試值)}")

# %% [markdown]
# 完整結構：
#
# ```python
# try:
#     危險的事()
# except 特定錯誤 as 錯誤:
#     處理(錯誤)
# except (錯誤A, 錯誤B):        # 一次接多種
#     處理()
# else:
#     沒出錯才做的事()            # 少用，但很精確
# finally:
#     一定會做的事()              # 收尾，出不出錯都執行
# ```

# %%
def 示範(值):
    try:
        結果 = 100 / 值
    except ZeroDivisionError:
        print("  except：除以零了")
    else:
        print("  else  ：沒出錯，結果是", 結果)
    finally:
        print("  finally：不管怎樣都會執行")


print("值 = 5")
示範(5)
print("\n值 = 0")
示範(0)

# %% [markdown]
# ### ⚠️ 三個禁忌

# %%
# ❌ 禁忌一：裸 except（連 Ctrl+C 都接住，程式變成按不停的殭屍）
# try: ...
# except: ...                 # 至少要寫 except Exception:

# ❌ 禁忌二：吞掉例外
def 存檔_壞範例(資料):
    try:
        raise OSError("磁碟滿了")
    except Exception:
        pass                   # 資料沒存到，而且你永遠不會知道


存檔_壞範例("重要資料")
print("🔴 程式看起來一切正常…但資料根本沒存。這是所有 debug 惡夢的源頭。")

# %%
# ✔ 如果真的要忽略，至少記下來
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", force=True)


def 存檔_好範例(資料):
    try:
        raise OSError("磁碟滿了")
    except OSError as 錯誤:
        logging.warning("存檔失敗：%s", 錯誤)


存檔_好範例("重要資料")

# %% [markdown]
# **❌ 禁忌三：`try` 包太大**
#
# ```python
# try:
#     讀檔(); 計算(); 存檔(); 寄信()
# except Exception:
#     print("出錯了")        # 哪一步出錯？不知道
# ```
#
# **`try` 要包「剛好可能出錯的那幾行」，不是整個函式。**

# %% [markdown]
# ## 11.4 常見例外一覽

# %%
測試 = [
    ("int('兩杯')", lambda: int("兩杯")),
    ("'a' + 1", lambda: "a" + 1),
    ("MENU['綠茶']", lambda: MENU["綠茶"]),
    ("[1,2][10]", lambda: [1, 2][10]),
    ("None.strip()", lambda: None.strip()),
    ("open('不存在.csv')", lambda: open("不存在.csv")),
    ("1 / 0", lambda: 1 / 0),
]

for 說明, 動作 in 測試:
    try:
        動作()
    except Exception as 錯誤:
        print(f"{說明:<22} → {type(錯誤).__name__}")

# %% [markdown]
# **它們有階層關係：**
#
# ```
# BaseException
#  └── Exception              ← 你該接的層級
#       ├── ValueError
#       ├── LookupError
#       │    ├── KeyError
#       │    └── IndexError
#       ├── OSError
#       │    └── FileNotFoundError
#       └── ...
#  ├── KeyboardInterrupt      ← 不要接這些
#  └── SystemExit
# ```

# %%
# 所以 except LookupError 會同時接住 KeyError 和 IndexError
for 動作 in [lambda: MENU["綠茶"], lambda: [1, 2][10]]:
    try:
        動作()
    except LookupError as 錯誤:
        print("被 LookupError 接住：", type(錯誤).__name__)

print("\n驗證階層：", KeyError.__mro__[:4])

# %% [markdown]
# ⚠️ **`except` 的順序：從最 specific 到最一般。**
# 把 `except Exception` 寫在前面，下面的分支永遠不會執行。

# %% [markdown]
# ## 11.5 raise：主動拋出例外

# %%
def 設定數量(數量):
    if 數量 <= 0:
        raise ValueError(f"數量必須大於 0，收到 {數量}")
    return 數量


try:
    設定數量(0)
except ValueError as 錯誤:
    print("🔴", 錯誤)

# %% [markdown]
# > 🔍 **什麼時候該拋、什麼時候該回傳預設值？**
# >
# > | 情況 | 做法 |
# > | --- | --- |
# > | 呼叫方給的資料就是錯的（程式 bug） | **`raise`**，讓它立刻爆 |
# > | 正常業務情境的「找不到」 | 回傳 `None` 或預設值 |
# >
# > `price_of("綠茶")` 綠茶不在菜單 → 代表點餐系統讓客人點了不存在的東西，是 bug，該 `raise`。
# > `找會員("0912…")` 查不到 → 新客人很正常，回傳 `None`。
# >
# > **最糟的做法是「出錯了但回傳 0」**，那會讓錯誤在系統裡默默擴散。

# %% [markdown]
# ### 自訂例外

# %%
class 庫存不足(Exception):
    """庫存不足以完成這筆訂單。"""


class 品項不存在(Exception):
    """菜單上沒有這個品項。"""


def 下單(品項, 數量, 庫存):
    if 品項 not in MENU:
        raise 品項不存在(f"菜單上沒有 {品項}")
    if 庫存.get(品項, 0) < 數量:
        raise 庫存不足(f"{品項} 只剩 {庫存.get(品項, 0)} 杯，你要 {數量} 杯")
    return f"{品項} x{數量} 下單成功"


庫存 = {"珍珠奶茶": 3, "冬瓜檸檬": 10}

for 品項, 數量 in [("珍珠奶茶", 2), ("珍珠奶茶", 5), ("綠茶", 1)]:
    try:
        print("🟢", 下單(品項, 數量, 庫存))
    except 庫存不足 as 錯誤:
        print("⚠️ 給客人的友善訊息：", 錯誤)
    except 品項不存在 as 錯誤:
        print("🐞 這是我們的 bug，要記錄：", 錯誤)

# %% [markdown]
# 自訂例外的價值：**呼叫方可以精準地處理特定狀況**。
# 比起全部都拋 `ValueError` 然後用字串比對訊息，這乾淨太多了。

# %%
# raise ... from：保留原因，traceback 會顯示「根本原因」
def price_of(品項, 杯型):
    try:
        return MENU[品項][杯型]
    except KeyError as 錯誤:
        raise 品項不存在(f"菜單上沒有 {品項} / {杯型}") from 錯誤


try:
    price_of("綠茶", "大杯")
except 品項不存在 as 錯誤:
    print("🔴", 錯誤)
    print("   根本原因：", repr(錯誤.__cause__), "← from 保留下來的")

# %% [markdown]
# ## 11.6 🧪 測試例外：這是重點
#
# **「錯誤處理」也是功能，也要測。** 而且通常是最容易被忘記測的部分。

# %%
# 純 assert 版本（Notebook 裡最方便，不用裝 pytest）
def test_數量為零要拋出ValueError():
    try:
        設定數量(0)
    except ValueError:
        return                                     # 🟢 正確拋出
    raise AssertionError("應該要拋出 ValueError")    # 🔴 沒拋出就是錯


test_數量為零要拋出ValueError()
print("🟢 通過")

# %%
# unittest 版本（標準庫）
import unittest


class Test下單(unittest.TestCase):
    def setUp(self):
        self.庫存 = {"珍珠奶茶": 3}

    def test_庫存足夠可以下單(self):
        self.assertIn("下單成功", 下單("珍珠奶茶", 2, self.庫存))

    def test_庫存不足要拋出庫存不足(self):
        with self.assertRaises(庫存不足):
            下單("珍珠奶茶", 5, self.庫存)

    def test_錯誤訊息要包含剩餘數量(self):
        with self.assertRaises(庫存不足) as 捕捉:
            下單("珍珠奶茶", 5, self.庫存)
        self.assertIn("只剩 3 杯", str(捕捉.exception))

    def test_不存在的品項要拋出品項不存在(self):
        with self.assertRaises(品項不存在):
            下單("綠茶", 1, self.庫存)


unittest.main(argv=[""], exit=False, verbosity=2)

# %% [markdown]
# pytest 版本：
#
# ```python
# def test_庫存不足要拋出庫存不足():
#     with pytest.raises(庫存不足, match="只剩 3 杯"):
#         下單("珍珠奶茶", 5, {"珍珠奶茶": 3})
# ```
#
# > ⚠️ **常見錯誤：只測成功路徑。**
# > 你的程式有一半的程式碼在處理「不正常」。
# > **每寫一個 `raise`，就配一個測試。**
#
# ### 測試清單：每個函式問自己
#
# | 問題 | 例子 |
# | --- | --- |
# | 正常輸入？ | `price_of("珍珠奶茶", "大杯")` |
# | 空的輸入？ | `總營收([])` |
# | 邊界值？ | `結帳(199)` / `結帳(200)` |
# | 型別錯誤？ | `設定數量("兩杯")` |
# | 不存在的東西？ | `price_of("綠茶", "大杯")` |
# | 負數 / 零？ | `設定數量(-1)` |

# %% [markdown]
# ## 11.7 讀懂 Traceback

# %%
import traceback


def 計算小計(訂單):
    return MENU[訂單["品項"]][訂單["杯型"]] * 訂單["數量"]


def 結帳(訂單):
    return 計算小計(訂單)


try:
    結帳({"品項": "珍珠奶茶", "杯型": "特大杯", "數量": 2})
except KeyError:
    print(traceback.format_exc())

# %% [markdown]
# **閱讀方法：**
#
# 1. **先看最後一行**：`KeyError: '特大杯'` ← 發生什麼事
# 2. **再看倒數第二段**：在哪個函式、哪一行爆的
# 3. **`^^^^` 標記**（Python 3.11+）直接指出是哪個運算式失敗
# 4. **上面幾段是「怎麼走到這裡的」**：`<module>` → `結帳` → `計算小計`
#
# > 🔍 **最常見的閱讀錯誤：從第一行開始讀。**
# > 第一行只是說「這是個 traceback」。**真正的錯誤永遠在最後一行。**

# %% [markdown]
# ## 11.8 除錯工具

# %%
# 第 0 級：print 大法（誠實地說，最常用）
訂單 = {"品項": "珍珠奶茶", "杯型": "特大杯"}
print(f"{訂單=}")
print(f"{list(MENU.keys())=}")
print(f"{list(MENU['珍珠奶茶'].keys())=}   ← 一眼看出「特大杯」不在裡面")

# %%
# 第 1 級：logging（正式程式用這個）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    force=True,
)

logging.debug("細節，開發時看（現在 level=INFO，所以看不到）")
logging.info("正常流程：訂單 %s 已建立", "A001")
logging.warning("庫存只剩 %d", 3)
logging.error("存檔失敗：%s", "磁碟滿了")

# %% [markdown]
# **`logging` 比 `print` 好在哪？**
#
# | | print | logging |
# | --- | --- | --- |
# | 關掉 | 要一行行刪 | 改一個 level |
# | 分級 | 沒有 | DEBUG/INFO/WARNING/ERROR |
# | 時間戳記 | 自己加 | 自動 |
# | 輸出到檔案 | 自己寫 | 一行設定 |
#
# ⚠️ **注意寫法**：`logging.info("訂單 %s", 編號)` 而不是 f-string。
# 這樣在 level 不夠時，字串根本不會被組出來，省效能。

# %% [markdown]
# **第 2 級：`breakpoint()`**
#
# ```python
# def 計算小計(訂單):
#     breakpoint()          # 執行到這裡會停下來，進入互動模式
#     return MENU[訂單["品項"]][訂單["杯型"]]
# ```
#
# | 指令 | 意思 |
# | --- | --- |
# | `n` | 下一行 | `s` | 進入函式 | `c` | 繼續 |
# | `p 變數` | 印出變數 | `l` | 看現在在哪 | `q` | 離開 |
#
# ⚠️ 在 Jupyter 裡會開啟互動框，**自動化執行時會卡住**，所以本教材的 notebook 不用它。

# %% [markdown]
# ### 第 3 級：寫一個測試重現它 —— **最有價值的除錯法**

# %%
# 阿宏回報：「有時候會員價算錯」
# 不要用 print 猜，先寫一個測試把它釘死：


def test_會員買大杯珍奶是59元():
    assert price_of_with_member("珍珠奶茶", "大杯", True) == 59


def price_of_with_member(品項, 杯型, 是會員):
    價格 = MENU[品項][杯型]
    return round(價格 * 0.9) if 是會員 else 價格         # 🐞 bug：round(58.5) = 58


try:
    test_會員買大杯珍奶是59元()
except AssertionError:
    print("🔴 重現了！實際算出：", price_of_with_member("珍珠奶茶", "大杯", True))

# %%
# 修好
from decimal import Decimal, ROUND_HALF_UP


def price_of_with_member(品項, 杯型, 是會員):
    價格 = MENU[品項][杯型]
    if 是會員:
        return int(Decimal(str(價格 * 0.9)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return 價格


test_會員買大杯珍奶是59元()
print("🟢 修好了，而且這個 bug 永遠不會再回來 —— 因為測試留下來了。")

# %% [markdown]
# > 🔍 **這叫「回歸測試」(regression test)。**
# > 每修一個 bug 就留下一個測試，你的測試套件會慢慢變成
# > 一份「這個系統踩過的所有坑」的清單。**一年後你會非常感謝當初寫下它們的自己。**

# %% [markdown]
# ## 11.9 🟢 把點餐機修好

# %%
class 輸入錯誤(Exception):
    """使用者輸入的資料不合法。"""


def 解析數量(輸入值: str) -> int:
    """把使用者輸入轉成數量。

    >>> 解析數量("2")
    2
    >>> 解析數量(" 3 ")
    3
    """
    文字 = 輸入值.strip()
    try:
        數量 = int(文字)
    except ValueError as 錯誤:
        raise 輸入錯誤(f"數量請輸入數字，你輸入的是「{文字}」") from 錯誤

    if 數量 <= 0:
        raise 輸入錯誤(f"數量必須大於 0，你輸入的是 {數量}")
    if 數量 > 50:
        raise 輸入錯誤(f"單筆最多 50 杯，你輸入的是 {數量}")
    return 數量


for 輸入值 in ["2", " 3 ", "兩杯", "0", "51", "50"]:
    try:
        print(f"輸入 {輸入值!r:<8} → 🟢 {解析數量(輸入值)}")
    except 輸入錯誤 as 錯誤:
        print(f"輸入 {輸入值!r:<8} → ⚠️ {錯誤}")

# %% [markdown]
# **點餐機的主程式（互動層）負責接住錯誤，不讓它炸到客人臉上：**
#
# ```python
# def 點餐機迴圈():
#     while True:
#         輸入值 = input("請輸入數量：")
#         try:
#             return 解析數量(輸入值)
#         except 輸入錯誤 as 錯誤:
#             print(f"⚠️ {錯誤}")        # 友善訊息，繼續問
# ```
#
# > 🔍 **注意這個分工：**
# >
# > - `解析數量()` 是**純函式**，只負責判斷和拋錯 → **超好測**
# > - `點餐機迴圈()` 負責互動和顯示 → 不用測（也很難測）
# >
# > **把「決定」和「互動」分開**，是讓程式可測試的關鍵設計，
# > 也是第 6、9 章反覆出現的同一個原則。

# %%
# 六個測試，涵蓋正常、空白、型別錯誤、邊界
def 測試解析數量():
    assert 解析數量("2") == 2
    assert 解析數量(" 3 ") == 3
    assert 解析數量("50") == 50                  # 邊界：剛好可以

    for 壞輸入 in ["兩杯", "0", "-1", "51", ""]:
        try:
            解析數量(壞輸入)
        except 輸入錯誤:
            continue
        raise AssertionError(f"{壞輸入!r} 應該要被拒絕")


測試解析數量()
print("🟢 六類情況全部通過 —— 這才是完整的測試")

# %% [markdown]
# ## 📌 本章速記
#
# ```python
# # EAFP：先做，出事再說（Python 風格）
# try: 價格 = MENU[品項][杯型]
# except KeyError: ...
#
# # ⚠️ 三個禁忌
# except:                    # 裸 except → 至少 except Exception
# except Exception: pass     # 吞掉例外 → 至少 logging
# try: 包住整個函式            # → 只包可能出錯的那幾行
#
# # 主動拋出
# raise ValueError(f"數量必須大於 0，收到 {數量}")
# raise 自訂錯誤("訊息") from 原本的錯誤
# class 庫存不足(Exception): ...
#
# # 測試例外（每個 raise 配一個測試！）
# with pytest.raises(ValueError, match="必須大於 0"): ...
# with self.assertRaises(ValueError): ...
#
# # 讀 traceback：從最後一行往上讀
#
# # 除錯四級
# print(f"{變數=}") → logging.info("訂單 %s", 編號) → breakpoint() → 寫測試重現
# ```

# %% [markdown]
# ---
# ## 🧪 練習

# %% [markdown]
# ### 練習 11-1：安全的平均
# 空清單時回傳 0，不要爆炸。

# %%
def 安全平均(訂單):
    pass  # 👉 你的實作


try:
    assert 安全平均([100, 200]) == 150
    assert 安全平均([]) == 0
    print("🟢 11-1 通過")
except (AssertionError, TypeError):
    print("🔴 還沒做或不正確")

# %% [markdown]
# ### 練習 11-2：自訂例外
# 寫 `扣庫存(庫存, 品項, 數量)`：品項不存在 → `品項不存在`；庫存不夠 → `庫存不足`（訊息含剩餘數量）；
# 正常 → 回傳扣除後的庫存 dict。

# %%
def 扣庫存(庫存: dict, 品項: str, 數量: int) -> dict:
    pass  # 👉 你的實作


def 測試扣庫存():
    庫存 = {"珍珠奶茶": 5}
    assert 扣庫存(庫存, "珍珠奶茶", 2) == {"珍珠奶茶": 3}

    for 錯誤型別, 參數 in [(品項不存在, ("綠茶", 1)), (庫存不足, ("珍珠奶茶", 99))]:
        try:
            扣庫存(庫存, *參數)
        except 錯誤型別:
            continue
        raise AssertionError(f"{參數} 應該拋出 {錯誤型別.__name__}")


try:
    測試扣庫存()
    print("🟢 11-2 通過")
except (AssertionError, TypeError) as 錯誤:
    print("🔴 還沒做或不正確：", 錯誤)

# %% [markdown]
# ### 練習 11-3：找出這段程式的三個問題
#
# ```python
# def 讀設定(路徑):
#     try:
#         with open(路徑) as f:
#             return json.load(f)
#     except:
#         return {}
# ```
#
# 👉 提示：裸 except、缺 encoding、吞掉例外。
#
# ### 練習 11-4：讀 traceback
#
# ```
# Traceback (most recent call last):
#   File "report.py", line 12, in <module>
#     print(日報表(今日訂單))
#   File "report.py", line 7, in 日報表
#     平均 = 總額 / len(訂單)
# ZeroDivisionError: division by zero
# ```
#
# 👉 錯誤是什麼？在哪一行？怎麼走到那裡的？根本原因是什麼？

# %% [markdown]
# ---
# ➡️ 下一章：`12-標準函式庫巡禮.ipynb` —— 你想自己刻的東西，Python 八成已經內建了。
