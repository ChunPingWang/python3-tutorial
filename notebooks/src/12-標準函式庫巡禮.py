# %% [markdown]
# # 第 12 章：標準函式庫巡禮 —— 別重造輪子
#
# > 🎬 **情境**
# > 阿宏一口氣丟來五個需求：
# >
# > 1. 報表要顯示「這是本月第幾天」「上週同一天是幾號」
# > 2. 菜單設定要能存檔、能讀回來（保留巢狀結構）
# > 3. 統計每個品項賣幾杯、前三名是誰
# > 4. 客人留的電話格式亂七八糟，要清洗成統一格式
# > 5. 算出中位數客單價（平均被幾筆大單拉高了）
#
# 你開始盤算「日期怎麼算閏年」「排序怎麼寫」…… **停。Python 都內建了。**
#
# 標準函式庫有 200 多個模組，**不用 `pip install`，在任何作業系統上都一樣**。

# %% [markdown]
# ## 12.1 datetime：日期與時間

# %%
from datetime import date, datetime, timedelta

今天 = date(2026, 9, 20)          # 教材固定用這天，結果才可重現
print("日期    :", 今天)
print("年月日  :", 今天.year, 今天.month, 今天.day)
print("weekday :", 今天.weekday(), "（0=週一 … 6=週日）")
print("今天是  :", ["週一", "週二", "週三", "週四", "週五", "週六", "週日"][今天.weekday()])
print("\n真正的今天：", date.today())

# %%
# 加減日期：timedelta —— 不用自己算月底幾天、不用判斷閏年
print("昨天      :", 今天 - timedelta(days=1))
print("上週同一天:", 今天 - timedelta(weeks=1))
print("30 天後   :", 今天 + timedelta(days=30))

跨月 = date(2026, 3, 1) - timedelta(weeks=1)
print("\n跨月測試：2026-03-01 的上週同一天 =", 跨月, "← 自動處理 2 月只有 28 天")

差距 = date(2026, 9, 30) - date(2026, 9, 1)
print("兩個日期相減 →", 差距, "，天數 =", 差距.days)

# %%
# 格式化與解析
print("isoformat（存檔一律用這個）:", 今天.isoformat())
print("給人看                    :", 今天.strftime("%Y年%m月%d日"))
print("從字串讀回                :", date.fromisoformat("2026-09-20"))
print("自訂格式解析              :", datetime.strptime("2026/09/20", "%Y/%m/%d").date())

# %% [markdown]
# | 格式碼 | 意思 |
# | --- | --- |
# | `%Y` `%m` `%d` | 年(4位) 月 日 |
# | `%H` `%M` `%S` | 時 分 秒 |
# | `%A` `%a` | 星期全名 / 縮寫 |
# | `%B` `%b` | 月份全名 / 縮寫 |
#
# ⚠️ **`strftime` 的輸出會受系統語系影響**（`%A` 在不同機器可能是 `Sunday` 或 `週日`）。
# 要跨平台一致，**自己做對照表**。

# %%
print("這台機器的 %A 輸出：", 今天.strftime("%A"), "← 換一台可能不一樣")
星期名 = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
print("自己做對照表      ：", 星期名[今天.weekday()], "← 永遠一樣")

# %% [markdown]
# ### ⚠️ 測試和日期：最容易出事的組合

# %%
# ✖ 無法測試：結果取決於「今天是星期幾」
def 是週末_壞版本():
    return date.today().weekday() >= 5


print("這個函式的測試，週一到週五會過，週六日會失敗：", 是週末_壞版本())


# ✔ 可測試：把「哪一天」當成參數
def 是週末(某天: date) -> bool:
    return 某天.weekday() >= 5


assert 是週末(date(2026, 9, 19)) is True      # 週六
assert 是週末(date(2026, 9, 20)) is True      # 週日
assert 是週末(date(2026, 9, 21)) is False     # 週一
print("🟢 現在永遠可預測了")

# %% [markdown]
# > 🔍 **這是 TDD 帶來的重要設計原則：把「不可控的東西」變成參數。**
# >
# > 時間、亂數、檔案、網路，都是不可控的。
# > 一旦把它們變成參數，你的函式就從「有時候會壞的」變成「永遠可預測的」。

# %% [markdown]
# ## 12.2 json：巢狀資料存檔（第 9 章講過，這裡補三個重點）

# %%
import json

菜單 = {"珍珠奶茶": {"中杯": 55, "大杯": 65}}

print("1. 中文一定要 ensure_ascii=False")
print("   不加：", json.dumps(菜單))
print("   加了：", json.dumps(菜單, ensure_ascii=False))

print("\n2. sort_keys=True 讓 git diff 乾淨")
print(json.dumps({"b": 1, "a": 2}, sort_keys=True))

print("\n3. JSON 不認識 date / set / Decimal")
try:
    json.dumps({"日期": date.today()})
except TypeError as 錯誤:
    print("   🔴 TypeError：", 錯誤)
print("   ✔ 解法：", json.dumps({"日期": date.today().isoformat()}))

# %% [markdown]
# ## 12.3 collections：Counter 與 defaultdict

# %%
from collections import Counter, defaultdict

訂單 = ["珍奶", "紅茶", "珍奶", "冬瓜", "珍奶", "紅茶"]

計數 = Counter(訂單)
print(計數)
print("珍奶賣了     :", 計數["珍奶"])
print("綠茶賣了     :", 計數["綠茶"], "← 不存在也不會 KeyError！")
print("前兩名       :", 計數.most_common(2))
print("總杯數       :", 計數.total())

# %% [markdown]
# 手寫版要 4 行，`Counter` 一行。而且 `most_common()` 直接給你排行榜。

# %%
訂單資料 = [("2026-09-19", 65), ("2026-09-20", 45), ("2026-09-19", 55)]

# 😩 一般字典
每日營收 = {}
for 日期, 金額 in 訂單資料:
    if 日期 not in 每日營收:
        每日營收[日期] = []
    每日營收[日期].append(金額)

# 🙂 defaultdict：查不到的鍵自動變成 []
每日營收2 = defaultdict(list)
for 日期, 金額 in 訂單資料:
    每日營收2[日期].append(金額)

print(dict(每日營收2))
assert 每日營收 == 每日營收2
print("🟢 結果一樣，少寫兩行")

# %%
# defaultdict(int) 拿來累加
每日合計 = defaultdict(int)
for 日期, 金額 in 訂單資料:
    每日合計[日期] += 金額
print(dict(每日合計))

# ⚠️ 副作用：光是「查詢」不存在的鍵，就會把它建立起來
d = defaultdict(int)
print("\n查詢 d['不存在'] →", d["不存在"])
print("字典現在變成      →", dict(d), "← 被建立了！")
print("要純查詢請用 .get()，或改用普通 dict。")

# %% [markdown]
# ## 12.4 statistics：正確的統計

# %%
import statistics as st

客單價 = [65, 45, 55, 65, 500]         # 最後那筆是團購

print("平均數 mean  :", st.mean(客單價), "← 被團購拉高了")
print("中位數 median:", st.median(客單價), "← 比較真實")
print("眾數   mode  :", st.mode(客單價))
print("標準差 stdev :", round(st.stdev(客單價), 1))

# %% [markdown]
# > 🔍 **為什麼阿宏要中位數？**
# > 五個客人裡有一個團購 500 元，平均就變成 146，但實際上根本沒人花 146。
# > **中位數（把數字排好，取中間那個）不受極端值影響。**
# >
# > 判斷準則：**資料有極端值就看中位數，分布平均就看平均數。**

# %%
# ⚠️ 空清單會拋 StatisticsError
try:
    st.median([])
except st.StatisticsError as 錯誤:
    print("🔴 StatisticsError：", 錯誤)


def 安全中位數(資料):
    return st.median(資料) if 資料 else 0


assert 安全中位數([]) == 0
assert 安全中位數([1, 2, 3]) == 2
print("🟢 加上邊界保護")

# %% [markdown]
# ## 12.5 re：正規表示式（清洗資料）
#
# 阿宏的客人電話欄位長這樣：
# `"0912345678"` `"0912-345-678"` `"(02)2345-6789"` `"+886912345678"` `"0912 345 678"`
#
# 你要統一成 `0912345678`。

# %%
import re


def 清洗電話(原始: str) -> str:
    數字 = re.sub(r"\D", "", 原始)            # 把所有「非數字」換成空字串
    if 數字.startswith("886"):
        數字 = "0" + 數字[3:]
    return 數字


案例 = [
    ("0912345678", "0912345678"),
    ("0912-345-678", "0912345678"),
    ("(02)2345-6789", "0223456789"),
    ("+886912345678", "0912345678"),
    ("0912 345 678", "0912345678"),
    ("", ""),                                 # 邊界
]

for 原始, 期望 in 案例:
    實際 = 清洗電話(原始)
    狀態 = "🟢" if 實際 == 期望 else "🔴"
    print(f"{狀態} {原始!r:<18} → {實際!r}")
    assert 實際 == 期望

# %% [markdown]
# ### 最常用的五個函式
#
# ```python
# re.sub(樣式, 取代, 字串)      # 取代 ← 清洗資料最常用
# re.search(樣式, 字串)         # 找第一個，回傳 Match 或 None
# re.findall(樣式, 字串)        # 找全部，回傳 list
# re.match(樣式, 字串)          # 從「開頭」比對
# re.fullmatch(樣式, 字串)      # 整個字串完全符合 ← 驗證格式用這個
# ```
#
# ### 最常用的樣式
#
# | 樣式 | 意思 |
# | --- | --- |
# | `\d` `\D` | 數字 / 非數字 |
# | `\w` `\s` | 字母數字底線 / 空白 |
# | `.` | 任何字元 |
# | `*` `+` `?` | 0 次以上 / 1 次以上 / 0 或 1 次 |
# | `{n}` `{n,m}` | 剛好 n 次 / n 到 m 次 |
# | `^` `$` | 開頭 / 結尾 |
# | `[abc]` `[^abc]` | 其中一個 / 不是其中任一 |
# | `(...)` | 群組，用 `.group(1)` 取出 |

# %%
# 驗證手機格式
for 電話 in ["0912345678", "0912-345-678", "12345"]:
    結果 = re.fullmatch(r"09\d{8}", 電話)
    print(f"{電話!r:<16} 是合法手機嗎？{'🟢 是' if 結果 else '🔴 否'}")

# %%
# 抓出訂單編號裡的日期（群組）
m = re.search(r"(\d{4})(\d{2})(\d{2})", "ORD-20260920-001")
print("完整比對：", m.group(0))
print("年/月/日 ：", m.group(1), m.group(2), m.group(3))
print("全部群組 ：", m.groups())

# %% [markdown]
# ⚠️ **一律用 `r"..."` 原始字串寫樣式**，否則 `\d` 的反斜線會被 Python 先吃掉一層。
#
# > ⚠️ **不要用 re 做所有事。**
# > 解析 HTML 用 HTML 解析器、解析 CSV 用 `csv`、解析 JSON 用 `json`。
# > re 適合「格式簡單且固定的文字」。
# >
# > 有句名言：「你用正規表示式解決了一個問題，現在你有兩個問題了。」
#
# ### 🧪 測試 re：一定要用參數化
#
# 正規表示式是最容易寫錯的東西。上面那六個案例就是一組參數化測試 ——
# pytest 版本長這樣：
#
# ```python
# @pytest.mark.parametrize("原始,期望", [
#     ("0912345678", "0912345678"),
#     ("(02)2345-6789", "0223456789"),
#     ("", ""),
# ])
# def test_清洗電話(原始, 期望):
#     assert 清洗電話(原始) == 期望
# ```

# %% [markdown]
# ## 12.6 itertools：組合與分組

# %%
from itertools import chain, groupby, islice, product

print("所有組合 product：")
for 組合 in product(["珍奶", "紅茶"], ["中杯", "大杯"]):
    print("  ", 組合)

print("\n串起來 chain  :", list(chain([1, 2], [3, 4])))
print("只取前 5 個 islice:", list(islice(range(1_000_000), 5)), "← 不會真的產生一百萬個")

# %%
# ⚠️ groupby 的大坑：它只把「相鄰」的相同元素分在一起
訂單明細 = [
    {"品項": "珍奶", "金額": 65},
    {"品項": "紅茶", "金額": 35},
    {"品項": "珍奶", "金額": 55},
]

print("沒先排序（錯誤）：")
for 品項, 群組 in groupby(訂單明細, key=lambda x: x["品項"]):
    print("  ", 品項, [g["金額"] for g in 群組])

print("\n先排序（正確）：")
已排序 = sorted(訂單明細, key=lambda x: x["品項"])
for 品項, 群組 in groupby(已排序, key=lambda x: x["品項"]):
    print("  ", 品項, [g["金額"] for g in 群組])

print("\n💡 實務上，分組用 defaultdict(list) 通常比 groupby 好懂。")

# %% [markdown]
# ## 12.7 random：亂數（以及怎麼測試它）

# %%
import random

rng = random.Random(42)                       # 獨立的、可重現的產生器
print("randint :", rng.randint(1, 10))
print("choice  :", rng.choice(["珍奶", "紅茶", "冬瓜"]))
print("sample  :", rng.sample(["A", "B", "C", "D"], 2))

# %%
# ⚠️ 亂數讓測試無法重現 —— 解法：把亂數來源變成參數
def 抽獎(名單, 抽幾個, rng=random):            # 預設用全域 random
    return rng.sample(名單, 抽幾個)


def test_抽獎結果可重現():
    名單 = ["A", "B", "C", "D", "E"]
    第一次 = 抽獎(名單, 2, rng=random.Random(42))
    第二次 = 抽獎(名單, 2, rng=random.Random(42))
    assert 第一次 == 第二次, "同樣的種子應該給同樣的結果"


test_抽獎結果可重現()
print("🟢 同樣種子 →", 抽獎(["A", "B", "C", "D", "E"], 2, rng=random.Random(42)))
print("   不同種子 →", 抽獎(["A", "B", "C", "D", "E"], 2, rng=random.Random(7)))

# %% [markdown]
# > 🔍 **和日期問題是同一個道理：把不可控的東西變成參數。**
# >
# > 這個技巧叫「依賴注入」（dependency injection），聽起來很高級，
# > 但你看到了，它其實只是「多一個參數」而已。**TDD 會自然而然把你推向這種設計。**

# %% [markdown]
# ## 12.8 其他值得知道的
#
# | 模組 | 用途 |
# | --- | --- |
# | `math` | `sqrt`、`ceil`、`floor`、`isclose`、`pi` |
# | `decimal` | 精確小數（金額計算，全書都在用） |
# | `argparse` | 命令列參數解析（做 CLI 工具必備） |
# | `enum` | 列舉（取代到處都是的字串常數） |
# | `functools` | `lru_cache`（快取）、`partial` |
# | `zoneinfo` | 時區（3.9+，取代第三方 pytz） |
# | `sqlite3` | **內建資料庫**，不用安裝任何東西 |

# %%
# enum：取代字串常數
from enum import Enum


class 杯型(Enum):
    中杯 = "中杯"
    大杯 = "大杯"


print("正確用法：", 杯型.大杯, "值 =", 杯型.大杯.value)

try:
    杯型.大盃                                  # 打錯字
except AttributeError as 錯誤:
    print("🟢 打錯字立刻爆：", 錯誤)
print("   （如果用字串，'大盃' 會默默流進系統，三個月後才發現）")

# %%
# functools.lru_cache：一行加上快取
import time
from functools import lru_cache


@lru_cache(maxsize=128)
def 很慢的查詢(品項):
    time.sleep(0.05)                           # 假裝很慢
    return len(品項) * 10


開始 = time.perf_counter()
很慢的查詢("珍珠奶茶")
第一次 = time.perf_counter() - 開始

開始 = time.perf_counter()
很慢的查詢("珍珠奶茶")                           # 同樣參數，直接回傳快取
第二次 = time.perf_counter() - 開始

print(f"第一次：{第一次 * 1000:.1f} ms")
print(f"第二次：{第二次 * 1000:.4f} ms ← 快取命中")
print("\n⚠️ 只能用在純函式上。會讀檔案或資料庫的函式加了快取，就會拿到過期資料。")

# %% [markdown]
# ## 📌 本章速記
#
# ```python
# # datetime
# date.today()  今天.weekday()  今天.isoformat()
# 今天 - timedelta(days=1)      date.fromisoformat("2026-09-20")
# # ⚠️ 把「今天」當參數傳進函式，否則無法測試
#
# # json
# json.dump(物件, f, ensure_ascii=False, indent=2, sort_keys=True)
# # ⚠️ date / set / Decimal 要先自己轉
#
# # collections
# Counter(清單).most_common(3)   # 排行榜
# defaultdict(list)              # 分組      defaultdict(int)  # 累加
#
# # statistics
# st.mean() st.median() st.mode() st.stdev()    # 有極端值看中位數
#
# # re
# re.sub(r"\D", "", 電話)         # 清洗
# re.fullmatch(r"09\d{8}", 電話)  # 驗證格式
# # ⚠️ 一律用 r"..."；每個規則都要有測試
#
# # itertools
# product() chain() islice()      # ⚠️ groupby 之前一定要先 sorted
#
# # random
# random.Random(42)               # 可重現的產生器 ← 測試用
#
# enum.Enum / functools.lru_cache / sqlite3
# ```

# %% [markdown]
# ---
# ## 🧪 練習

# %% [markdown]
# ### 練習 12-1：日期計算

# %%
def 第幾天(某天: date) -> int:
    pass  # 👉 你的實作


def 上週同一天(某天: date) -> date:
    pass  # 👉 你的實作


try:
    assert 第幾天(date(2026, 9, 20)) == 20
    assert 上週同一天(date(2026, 9, 20)) == date(2026, 9, 13)
    assert 上週同一天(date(2026, 3, 1)) == date(2026, 2, 22)      # 跨月！
    print("🟢 12-1 通過")
except (AssertionError, TypeError):
    print("🔴 還沒做或不正確")

# %% [markdown]
# ### 練習 12-2：銷售排行榜

# %%
def 排行榜(訂單, 前幾名):
    pass  # 👉 你的實作（提示：Counter）


try:
    assert 排行榜(["珍奶", "紅茶", "珍奶", "冬瓜", "珍奶", "紅茶"], 2) == [("珍奶", 3), ("紅茶", 2)]
    print("🟢 12-2 通過")
except (AssertionError, TypeError):
    print("🔴 還沒做或不正確")

# %% [markdown]
# ### 練習 12-3：清洗電話（已在 12.5 示範，自己再寫一次不要看答案）
#
# ### 練習 12-4：把不可測的函式改成可測的

# %%
def 今日優惠_壞版本():
    if date.today().weekday() == 2:            # 週三特價
        return 0.8
    return 1.0


# 👉 改寫成 今日優惠(某天) 並寫兩個測試


try:
    assert 今日優惠(date(2026, 9, 23)) == 0.8    # 2026-09-23 是週三
    assert 今日優惠(date(2026, 9, 21)) == 1.0    # 週一
    print("🟢 12-4 通過")
except NameError:
    print("🔴 還沒做：請定義 今日優惠(某天)")

# %% [markdown]
# ---
# ➡️ 下一章：`13-套件管理與-Jupyter-實務.ipynb` —— 阿宏要看圖表了。
