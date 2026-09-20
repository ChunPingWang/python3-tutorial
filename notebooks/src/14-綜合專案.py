# %% [markdown]
# # 第 14 章：綜合專案 —— 用 TDD 做出營運儀表板
#
# > 🎬 **情境（最終回）**
# > 阿宏：「下週要跟投資人開會。我要一份月報：每天的營收、熱銷前三名、滯銷品、
# > 會員佔比、客單價。要能從我 POS 匯出的 CSV 直接讀，而且小美用 Windows 也要能跑。」
#
# 這一章不教新語法。**你要把前 13 章的東西組合起來，交付一個真正的東西。**
#
# 我們完全按照 TDD 的節奏走：🔴 紅 → 🟢 綠 → 🔵 重構，一個功能一輪。

# %% [markdown]
# ## 14.1 第一步：把需求變成測試清單
#
# **不要先開檔案，先開一張清單。** 把阿宏的話翻譯成可驗證的句子：
#
# ```
# □ 能從菜單查出價格
# □ 會員滿 200 打 9 折，未滿不打
# □ 員工價 40 一律優先
# □ 一筆訂單知道自己的小計和應付金額
# □ 能把多筆訂單加總結帳
# □ 能算出：總營收、總杯數、客單價（平均與中位數）、會員佔比
# □ 能算出熱銷前三名
# □ 能算出完全沒賣的滯銷品
# □ 能把訂單存成 CSV，也能讀回來（而且讀回來要一模一樣）
# □ 能讀一整個資料夾的日報，產生月報
# □ 沒有訂單時不能崩潰
# □ 品項不存在時要明確報錯，不能默默算 0
# □ Windows / macOS / Linux 都要能跑
# ```
#
# > 🔍 **這張清單就是你的驗收標準，也是你的測試檔大綱。**
# > 每完成一項就劃掉一項。你永遠知道還剩多少，而且永遠有一個可執行的版本。
# >
# > 對比「先寫 800 行再執行」：你會在最後一刻同時面對 30 個 bug，而且不知道是哪一個造成的。

# %%
# 這個小工具讓 notebook 裡的紅綠燈看起來像真的測試框架
def 跑測試(*測試們):
    """執行一批測試函式，回報結果（這就是 pytest 骨架的最小版本）。"""
    通過 = 失敗 = 0
    for 測試 in 測試們:
        try:
            測試()
        except AssertionError as 錯誤:
            失敗 += 1
            print(f"  🔴 {測試.__name__}  {錯誤 or ''}")
        except Exception as 錯誤:
            失敗 += 1
            print(f"  🔴 {測試.__name__}  {type(錯誤).__name__}: {錯誤}")
        else:
            通過 += 1
            print(f"  🟢 {測試.__name__}")
    print(f"  ── 共 {通過 + 失敗} 個，通過 {通過}，失敗 {失敗}")
    return 失敗 == 0


print("測試執行器準備好了")

# %% [markdown]
# ## 14.2 🔴🟢🔵 第一輪：計價

# %% [markdown]
# ### 🔴 紅

# %%
def test_查得到菜單上的價格():
    assert unit_price("珍珠奶茶", "大杯") == 65


跑測試(test_查得到菜單上的價格)

# %% [markdown]
# ### 🟢 綠：寫剛好夠的

# %%
MENU = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
    "四季春茶": {"中杯": 30, "大杯": 35},
    "黑糖鮮奶": {"中杯": 60, "大杯": 70},
}


def unit_price(name, size):
    return MENU[name][size]


跑測試(test_查得到菜單上的價格)

# %% [markdown]
# ### 🔴 下一個：品項不存在時怎麼辦？
#
# **這是 TDD 逼你思考的地方。** 三個選項：
#
# | 選項 | 後果 |
# | --- | --- |
# | 回傳 0 | 阿宏少收錢三個月才發現 ❌ |
# | 回傳 None | 呼叫方忘記檢查 → 後面某處 `TypeError` ❌ |
# | **拋出例外** | 立刻爆、立刻知道 ✔ |

# %%
class DrinkShopError(Exception):
    """這個套件所有例外的共同父類別。"""


class MenuItemNotFound(DrinkShopError):
    """菜單上沒有這個品項或杯型。"""


class InvalidInput(DrinkShopError):
    """使用者輸入的資料不合法。"""


def test_品項不存在要拋出MenuItemNotFound():
    try:
        unit_price("綠茶", "大杯")
    except MenuItemNotFound:
        return
    raise AssertionError("應該要拋出 MenuItemNotFound")


跑測試(test_品項不存在要拋出MenuItemNotFound)

# %% [markdown]
# ### 🟢 綠

# %%
def unit_price(name, size):
    try:
        return MENU[name][size]
    except KeyError as exc:
        raise MenuItemNotFound(f"菜單上沒有「{name} / {size}」") from exc


跑測試(test_查得到菜單上的價格, test_品項不存在要拋出MenuItemNotFound)

# %% [markdown]
# ### 🔴 會員折扣：邊界三兄弟
#
# ⚠️ 注意 `65 * 0.9 = 58.5` —— **58.5 要變 58 還是 59？**
# 這就是第 2 章的銀行家捨入問題。阿宏說「都給我四捨五入」。

# %%
from decimal import ROUND_HALF_UP, Decimal


def round_half_up(value: float) -> int:
    """台灣人習慣的四捨五入（逢五進一）。"""
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def apply_member_discount(amount: int) -> int:
    if amount < 200:
        return amount
    return round_half_up(amount * 0.9)


def test_未達門檻不打折():
    assert apply_member_discount(199) == 199


def test_剛好達到門檻就打折():
    assert apply_member_discount(200) == 180


def test_超過門檻打折():
    assert apply_member_discount(500) == 450


def test_金額為零也不會出事():
    assert apply_member_discount(0) == 0


跑測試(test_未達門檻不打折, test_剛好達到門檻就打折, test_超過門檻打折, test_金額為零也不會出事)

# %% [markdown]
# ### 🔵 重構：把魔術數字變成常數

# %%
MEMBER_RATE = 0.9
MEMBER_THRESHOLD = 200
STAFF_PRICE = 40
TAX_RATE = 0.05


def apply_member_discount(amount: int) -> int:
    if amount < MEMBER_THRESHOLD:
        return amount
    return round_half_up(amount * MEMBER_RATE)


def line_price(name, size, quantity=1, *, is_member=False, is_staff=False) -> int:
    if quantity <= 0:
        raise ValueError(f"數量必須大於 0，收到 {quantity}")
    if is_staff:                                   # guard clause：員工價優先
        return STAFF_PRICE * quantity

    amount = unit_price(name, size) * quantity
    return apply_member_discount(amount) if is_member else amount


def test_一般客人依菜單計價():
    assert line_price("珍珠奶茶", "大杯", 2) == 130


def test_會員未滿門檻不打折():
    assert line_price("珍珠奶茶", "大杯", 2, is_member=True) == 130


def test_會員滿門檻才打折():
    assert line_price("珍珠奶茶", "大杯", 4, is_member=True) == 234


def test_員工價蓋過一切折扣():
    assert line_price("珍珠奶茶", "大杯", 2, is_member=True, is_staff=True) == 80


跑測試(test_未達門檻不打折, test_剛好達到門檻就打折,
     test_一般客人依菜單計價, test_會員未滿門檻不打折,
     test_會員滿門檻才打折, test_員工價蓋過一切折扣)

# %% [markdown]
# > 🔍 **注意重構的定義：改善結構，不改變行為。**
# >
# > 「把 `200` 改成 `MEMBER_THRESHOLD`」是重構；
# > 「把門檻從 200 改成 300」不是重構，那是改需求 —— 要先改測試。

# %% [markdown]
# ## 14.3 🔴🟢🔵 第二輪：訂單
#
# ### 🔴 測試決定了 Order 長什麼樣
#
# 第二個測試（內容相同就相等）就是在要求 `__eq__`，也就是在要求你用 `@dataclass`。

# %%
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Order:
    item: str
    size: str = "中杯"
    quantity: int = 1
    is_member: bool = False
    is_staff: bool = False
    toppings: list[str] = field(default_factory=list)      # ⚠️ 不能寫 = []
    ordered_on: date | None = None

    @property
    def unit(self) -> int:
        return unit_price(self.item, self.size)

    @property
    def subtotal(self) -> int:
        return self.unit * self.quantity

    @property
    def total(self) -> int:
        return line_price(self.item, self.size, self.quantity,
                          is_member=self.is_member, is_staff=self.is_staff)

    def __str__(self) -> str:
        return f"{self.item}({self.size}) x{self.quantity} = {self.total} 元"


def test_訂單會自己算應付金額():
    assert Order("珍珠奶茶", "大杯", 2).total == 130


def test_內容相同的兩筆訂單相等():
    assert Order("珍珠奶茶", "大杯", 2) == Order("珍珠奶茶", "大杯", 2)


def test_改了數量之後小計自動更新():
    o = Order("珍珠奶茶", "大杯")
    o.quantity = 3
    assert o.subtotal == 195


def test_每筆訂單有自己的加料清單():
    """可變預設值陷阱的回歸測試（第 6 章）。"""
    a, b = Order("珍珠奶茶"), Order("四季春茶")
    a.toppings.append("珍珠")
    assert b.toppings == []


跑測試(test_訂單會自己算應付金額, test_內容相同的兩筆訂單相等,
     test_改了數量之後小計自動更新, test_每筆訂單有自己的加料清單)

# %% [markdown]
# > 🔍 `test_每筆訂單有自己的加料清單` 看起來很蠢，
# > 但**它防的是第 6 章那個惡名昭彰的陷阱**。
# > **每個你踩過的坑，都值得留一個測試。**

# %% [markdown]
# ### 🔴 使用者輸入：把「決定」和「互動」分開
#
# ⚠️ `input()` 沒辦法測試（測試會卡住等輸入），所以它**不能**出現在這裡。

# %%
MAX_QUANTITY = 50


def parse_quantity(raw: str) -> int:
    """只負責「判斷」，不做任何互動 —— 所以測得動。"""
    text = raw.strip()
    try:
        quantity = int(text)
    except ValueError as exc:
        raise InvalidInput(f"數量請輸入數字，你輸入的是「{text}」") from exc

    if quantity <= 0:
        raise InvalidInput(f"數量必須大於 0，你輸入的是 {quantity}")
    if quantity > MAX_QUANTITY:
        raise InvalidInput(f"單筆最多 {MAX_QUANTITY} 杯，你輸入的是 {quantity}")
    return quantity


def test_正常的數字輸入():
    assert parse_quantity("2") == 2


def test_前後空白會被忽略():
    assert parse_quantity(" 3 ") == 3


def test_剛好等於上限可以接受():
    assert parse_quantity("50") == 50


def test_不合法的輸入一律拋出InvalidInput():
    for raw in ["兩杯", "", "  ", "0", "-1", "51", "3.5"]:
        try:
            parse_quantity(raw)
        except InvalidInput:
            continue
        raise AssertionError(f"{raw!r} 應該要被拒絕")


跑測試(test_正常的數字輸入, test_前後空白會被忽略,
     test_剛好等於上限可以接受, test_不合法的輸入一律拋出InvalidInput)

# %% [markdown]
# ```python
# # ✔ 可測試：只負責「判斷」
# def parse_quantity(raw: str) -> int: ...
#
# # ✖ 不可測試：混了「互動」
# def ask_quantity():
#     return int(input("請輸入數量："))
# ```
#
# **這是整個專案最重要的設計決策。**

# %% [markdown]
# ## 14.4 🔴🟢🔵 第三輪：報表
#
# ### 🔴 先寫最容易被忘記的測試：空的
#
# 打烊時如果一筆訂單都沒有，日報表不該掛掉。
# 「零筆資料」在真實世界絕對會發生（週一公休、颱風天）。

# %%
import statistics
from collections import Counter, defaultdict

WEEKDAY_NAMES = ("週一", "週二", "週三", "週四", "週五", "週六", "週日")


def revenue(orders) -> int:
    return sum(o.total for o in orders)


def cup_count(orders) -> int:
    return sum(o.quantity for o in orders)


def average_ticket(orders) -> int:
    return round(revenue(orders) / len(orders)) if orders else 0


def median_ticket(orders) -> int:
    return round(statistics.median(o.total for o in orders)) if orders else 0


def member_ratio(orders) -> float:
    return sum(1 for o in orders if o.is_member) / len(orders) if orders else 0.0


def cups_by_item(orders) -> Counter:
    counter: Counter = Counter()
    for o in orders:
        counter[o.item] += o.quantity
    return counter


def revenue_by_item(orders) -> dict:
    result = defaultdict(int)
    for o in orders:
        result[o.item] += o.total
    return dict(result)


def top_items(orders, n=3):
    return cups_by_item(orders).most_common(n)


def slow_movers(orders, catalog=None) -> set:
    catalog = catalog if catalog is not None else list(MENU)
    return set(catalog) - {o.item for o in orders}


def test_空訂單的營收是零():
    assert revenue([]) == 0


def test_空訂單的平均是零而不是除以零錯誤():
    assert average_ticket([]) == 0
    assert median_ticket([]) == 0


def test_沒有訂單時排行榜是空的():
    assert top_items([], 3) == []


跑測試(test_空訂單的營收是零, test_空訂單的平均是零而不是除以零錯誤, test_沒有訂單時排行榜是空的)

# %% [markdown]
# ### 🔴 為什麼要中位數
#
# 這個測試同時是程式碼和文件：它解釋了「為什麼我們要算兩種客單價」。

# %%
def test_中位數不會被團購拉走():
    orders = [
        Order("四季春茶", "中杯"),               # 30
        Order("珍珠奶茶", "中杯"),               # 55
        Order("珍珠奶茶", "大杯", 20),           # 1300 團購
    ]
    assert average_ticket(orders) == 462         # 被拉高了
    assert median_ticket(orders) == 55           # 比較真實


跑測試(test_中位數不會被團購拉走)

# %% [markdown]
# ### 🔴 日期不能依賴「今天」，星期名稱不能用 strftime
#
# - 如果 `daily_report` 內部用 `date.today()`，測試**今天會過、下週會掛** → 把日期變成參數 `on`
# - `strftime("%A")` 在你的 Mac 上是 `Sunday`，在別人機器上可能是 `週日` → 自己做對照表

# %%
def daily_report(orders, on: date) -> str:
    lines = [
        "=" * 34,
        f"{'阿宏手搖飲 日報表':^28}",
        f"{on.isoformat()}（{WEEKDAY_NAMES[on.weekday()]}）".center(30),
        "=" * 34,
        f"{'總營收':<12}{revenue(orders):>10,} 元",
        f"{'總杯數':<12}{cup_count(orders):>10,} 杯",
        f"{'訂單筆數':<11}{len(orders):>10,} 筆",
        f"{'平均客單價':<10}{average_ticket(orders):>10,} 元",
        f"{'中位數客單價':<9}{median_ticket(orders):>10,} 元",
        f"{'會員佔比':<11}{member_ratio(orders):>10.0%}",
        "-" * 34,
        f"{'熱銷排行':<12}",
    ]

    ranking = top_items(orders, 3)
    if ranking:
        for i, (name, cups) in enumerate(ranking, start=1):
            lines.append(f"  {i}. {name:<10}{cups:>4} 杯")
    else:
        lines.append("  （今天沒有訂單）")

    idle = slow_movers(orders)
    if idle:
        lines += ["-" * 34, f"滯銷品項：{'、'.join(sorted(idle))}"]

    lines.append("=" * 34)
    return "\n".join(lines)


REPORT_DAY = date(2026, 9, 20)          # 寫死的常數，測試才可重現


def 範例訂單():
    """每個測試呼叫它拿到一份全新的資料，避免測試互相影響。"""
    return [
        Order("珍珠奶茶", "大杯", 2, ordered_on=REPORT_DAY),        # 130
        Order("珍珠奶茶", "中杯", 1, ordered_on=REPORT_DAY),        # 55
        Order("四季春茶", "中杯", 3, ordered_on=REPORT_DAY),        # 90
        Order("冬瓜檸檬", "大杯", 1, is_member=True, ordered_on=REPORT_DAY),  # 45
    ]


def test_日報表包含關鍵數字():
    text = daily_report(範例訂單(), on=REPORT_DAY)
    assert "320" in text
    assert "2026-09-20" in text
    assert "珍珠奶茶" in text


def test_日報表的星期名稱不受系統語系影響():
    assert "週一" in daily_report([], on=date(2026, 9, 21))
    assert "週六" in daily_report([], on=date(2026, 9, 19))


def test_沒有訂單也能產出報表而不是崩潰():
    assert "今天沒有訂單" in daily_report([], on=REPORT_DAY)


跑測試(test_日報表包含關鍵數字, test_日報表的星期名稱不受系統語系影響,
     test_沒有訂單也能產出報表而不是崩潰)

# %%
print(daily_report(範例訂單(), on=REPORT_DAY))

# %% [markdown]
# > 🔍 **測試要測「行為」，不要測「長相」。**
# >
# > ```python
# > # ✖ 脆弱：改一個空格就壞
# > assert daily_report(...) == "==========\n  阿宏手搖飲...\n=========="
# >
# > # ✔ 穩健：測真正在意的東西
# > assert "320" in text
# > ```
# >
# > 排版是會改的，數字對不對才是重點。

# %% [markdown]
# ## 14.5 🔴🟢🔵 第四輪：存檔（跨平台的考驗）
#
# ### 🔴 最重要的一個測試：round-trip
#
# **「存進去再讀出來要一模一樣」** 是所有 I/O 程式的黃金測試。
# 它一口氣驗證了寫入格式、讀取解析、型別轉換、編碼，全部。

# %%
import csv
import tempfile
from pathlib import Path

FIELDNAMES = ["日期", "品項", "杯型", "數量", "會員", "金額"]


def save_orders(orders, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:      # ⚠️ 兩個參數都不能少
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for o in orders:
            writer.writerow({
                "日期": (o.ordered_on or date.today()).isoformat(),
                "品項": o.item,
                "杯型": o.size,
                "數量": o.quantity,
                "會員": "Y" if o.is_member else "N",
                "金額": o.total,
            })
    return path


def load_orders_第一版(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return [
            Order(item=r["品項"], size=r["杯型"], quantity=r["數量"],   # 🐞 忘了轉型
                  is_member=r["會員"] == "Y", ordered_on=r["日期"])
            for r in csv.DictReader(f)
        ]


def test_存檔再讀回來要一模一樣():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "訂單.csv"
        save_orders(範例訂單(), path)
        assert load_orders_第一版(path) == 範例訂單()


跑測試(test_存檔再讀回來要一模一樣)

# %% [markdown]
# ### 🔴 這個測試抓到什麼？
#
# **CSV 讀進來全部是字串。** `quantity='2'` 不等於 `quantity=2`。
#
# 這正是我們要這個測試的原因 —— 沒有它，這個 bug 會一路活到阿宏發現月報數字怪怪的。

# %%
def load_orders(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return [
            Order(
                item=r["品項"],
                size=r["杯型"],
                quantity=int(r["數量"]),                      # ← 補上轉型
                is_member=r["會員"] == "Y",
                ordered_on=date.fromisoformat(r["日期"]),      # ← 日期也要
            )
            for r in csv.DictReader(f)
        ]


def test_存檔再讀回來要一模一樣():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "訂單.csv"
        save_orders(範例訂單(), path)
        assert load_orders(path) == 範例訂單()


def test_讀回來的數量是整數不是字串():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "訂單.csv"
        save_orders(範例訂單(), path)
        loaded = load_orders(path)
    assert isinstance(loaded[0].quantity, int)
    assert isinstance(loaded[0].ordered_on, date)


跑測試(test_存檔再讀回來要一模一樣, test_讀回來的數量是整數不是字串)

# %% [markdown]
# ### 🔴 三個跨平台的回歸測試
#
# 這三個測試就是你的「小美保險」：你在 Mac 上開發，它們會在 Windows 上幫你驗證。

# %%
import json


def save_menu(menu, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def export_for_excel(rows, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:    # ⚠️ utf-8-sig
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_中文以utf8儲存():
    """Windows 預設編碼是 cp950，不明確指定的話中文會壞掉。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = save_orders(範例訂單(), Path(tmp) / "訂單.csv")
        raw = path.read_bytes()
    assert "珍珠奶茶".encode("utf-8") in raw


def test_給Excel的CSV帶有BOM():
    """沒有 BOM 的話，Excel 開中文 CSV 會是亂碼。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = export_for_excel([{"品項": "珍珠奶茶", "金額": 65}], Path(tmp) / "報表.csv")
        head = path.read_bytes()[:3]
    assert head == b"\xef\xbb\xbf"


def test_JSON裡的中文不是轉義序列():
    """忘記 ensure_ascii=False 的話會變成 \\u73cd\\u73e0。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = save_menu(MENU, Path(tmp) / "菜單.json")
        text = path.read_text(encoding="utf-8")
    assert "珍珠奶茶" in text and "\\u" not in text


def test_測試結束後不留垃圾檔():
    with tempfile.TemporaryDirectory() as tmp:
        path = save_orders(範例訂單(), Path(tmp) / "訂單.csv")
        assert path.exists()
    assert not path.exists()


跑測試(test_中文以utf8儲存, test_給Excel的CSV帶有BOM,
     test_JSON裡的中文不是轉義序列, test_測試結束後不留垃圾檔)

# %% [markdown]
# ⚠️ **絕對不要這樣測：**
#
# ```python
# def test_存檔():
#     save_orders(SAMPLE, "/tmp/訂單.csv")        # 🪟 Windows 沒有 /tmp
#     assert Path("/tmp/訂單.csv").exists()        # 而且測完垃圾檔留著
# ```
#
# 用 `tempfile.TemporaryDirectory()`（標準庫）或 pytest 的 `tmp_path`。

# %% [markdown]
# ## 14.6 交付：月報表

# %%
import random


def load_month(folder):
    folder = Path(folder)
    return {p.stem: load_orders(p) for p in sorted(folder.glob("*.csv"))}


def monthly_summary(by_day) -> dict:
    return {day: revenue(orders) for day, orders in sorted(by_day.items())}


def text_bar_chart(data, width=24) -> str:
    if not data:
        return "（沒有資料）"
    largest = max(data.values()) or 1
    return "\n".join(
        f"{label}  {'█' * round(value / largest * width)} {value:,}"
        for label, value in data.items()
    )


def 造假資料(某天, 筆數, 種子):
    """亂數種子是參數而不是寫死的 —— 這樣結果才可重現。"""
    rng = random.Random(種子)
    items = list(MENU)
    return [
        Order(item=rng.choice(items), size=rng.choice(["中杯", "大杯"]),
              quantity=rng.randint(1, 3), is_member=rng.random() < 0.4,
              ordered_on=某天)
        for _ in range(筆數)
    ]


def test_月報把每天的營收整理出來():
    by_day = {"2026-09-20": 範例訂單(), "2026-09-19": [Order("珍珠奶茶", "大杯")]}
    assert monthly_summary(by_day) == {"2026-09-19": 65, "2026-09-20": 320}


def test_月報按日期排序():
    assert list(monthly_summary({"2026-09-20": [], "2026-09-01": []})) == [
        "2026-09-01", "2026-09-20"
    ]


def test_空月報是空字典():
    assert monthly_summary({}) == {}


跑測試(test_月報把每天的營收整理出來, test_月報按日期排序, test_空月報是空字典)

# %%
# 端對端跑一次：造資料 → 存檔 → 讀回 → 出月報（全程在暫存目錄，不留垃圾）
from datetime import timedelta

with tempfile.TemporaryDirectory() as tmp:
    資料夾 = Path(tmp) / "2026-09"

    for 位移 in range(7):
        某天 = date(2026, 9, 14) + timedelta(days=位移)
        訂單 = 造假資料(某天, 筆數=8 + 位移, 種子=20260914 + 位移)
        save_orders(訂單, 資料夾 / f"{某天.isoformat()}.csv")

    每日 = load_month(資料夾)
    摘要 = monthly_summary(每日)

    print(f"{'阿宏手搖飲 月報表':^30}")
    print("=" * 38)
    print(text_bar_chart(摘要))
    print("=" * 38)
    print(f"合計 {sum(摘要.values()):,} 元，共 {len(摘要)} 天，"
          f"{sum(cup_count(o) for o in 每日.values()):,} 杯")
    print()
    print(daily_report(每日["2026-09-20"], on=date(2026, 9, 20)))

# %% [markdown]
# ## 14.7 🔵 最後一輪重構：檢查分層
#
# 功能都完成了，退一步看整個專案（完整版在 `examples/`）：
#
# ```
# drinkshop/
# ├── menu.py       📦 只有資料           → 阿宏調價只改這裡
# ├── errors.py     📦 只有例外定義
# ├── pricing.py    🧮 純函式             → 好測
# ├── orders.py     🧮 純函式 + dataclass  → 好測
# ├── report.py     🧮 純函式             → 好測
# ├── storage.py    💾 唯一碰硬碟的        → 用 tempfile 測
# └── cli.py        🖥 唯一做互動的        → 幾乎沒邏輯，不用測
# ```
#
# **自我檢查三個問題：**
#
# 1. **有沒有函式既算東西又存檔？** → 拆開
# 2. **有沒有函式偷看 `date.today()` 或 `random`？** → 變成參數
# 3. **有沒有測試需要真的建立檔案？** → 只有 `test_storage.py` 應該要

# %% [markdown]
# ## 14.8 跑完整的專案測試套件
#
# `examples/` 裡是這個專案的正式版本（拆成檔案、加上 CLI）。
# 下面直接執行它的測試套件。

# %%
import subprocess
import sys

專案 = Path("..") / "examples"

結果 = subprocess.run(
    [sys.executable, "run_tests.py", "--doctest"],
    cwd=專案, capture_output=True, text=True, encoding="utf-8",
)
print(結果.stdout[-1200:])

# %%
# 有裝 pytest 的話，跑真正的 pytest
結果 = subprocess.run(
    [sys.executable, "-m", "pytest", "-q"],
    cwd=專案, capture_output=True, text=True, encoding="utf-8",
)
if 結果.returncode == 0:
    print(結果.stdout[-600:])
else:
    print("⚪ 沒有安裝 pytest（或有測試沒過）。上面的 run_tests.py 已經驗證過同樣的事。")
    print("   要裝 pytest：!{sys.executable} -m pip install pytest")

# %%
# 也試試 CLI
結果 = subprocess.run(
    [sys.executable, "-m", "drinkshop.cli", "demo", "--count", "8"],
    cwd=專案, capture_output=True, text=True, encoding="utf-8",
)
print(結果.stdout or 結果.stderr)

# %% [markdown]
# ## 14.9 📌 這 14 章你學到的
#
# ### 語法
#
# 變數與型別 → 字串格式化 → 判斷 → 迴圈 → 資料結構 → 函式 → 模組 →
# 檔案 I/O → 類別 → 例外 → 標準函式庫 → 套件管理
#
# ### 但更重要的是這些
#
# | 原則 | 第幾章 | 一句話 |
# | --- | --- | --- |
# | **先寫測試，需求才會清楚** | 2、3 | 寫不出 `assert` 代表你還不知道要做什麼 |
# | **紅 → 綠 → 重構** | 4、7 | 沒有測試的重構叫「改東西然後祈禱」 |
# | **難測試 = 設計不好** | 6、9 | 這是免費的設計警報器 |
# | **把副作用推到邊界** | 8、9 | 讓 90% 的程式是純函式 |
# | **把不可控的變成參數** | 12 | 時間、亂數、檔案路徑 |
# | **每修一個 bug 留一個測試** | 11 | 測試套件會變成踩坑清單 |
# | **測試名稱就是規格書** | 7 | 永遠不會過期的文件 |
# | **跨平台靠 pathlib + encoding + CI** | 9、13 | 三件事解決 95% 的問題 |

# %% [markdown]
# ## 14.10 🧪 最終練習
#
# 1. **加一個功能**：阿宏要「本月與上月的營收比較」。
#    先寫測試（包含「上月沒有資料」的邊界），再實作。
#
# 2. **重構**：把 `daily_report` 的排版邏輯抽成 `format_table(rows)`，
#    確保所有測試依然全綠。
#
# 3. **抓 bug**：把 `MEMBER_THRESHOLD` 改成 300，看看哪幾個測試變紅。
#    它們是不是**剛好就是**你該改的那幾個？
#
# 4. **跨平台**：如果你有 Windows 電腦（或用 GitHub Actions），在上面跑一次 `pytest`。
#    全綠嗎？沒有的話，是哪一類問題？
#
# 5. **從零再做一次**：換一個題目（記帳本、書單、健身紀錄），用同樣的節奏：
#    需求清單 → 測試 → 實作 → 重構 → 分層。
#    **第二次你會快很多，而且那時候你才真的學會了。**

# %% [markdown]
# ---
# ## 🎉 恭喜你讀完了
#
# 一個建議：**找一件你每週都在手動做的事，把它自動化。**
#
# 整理下載資料夾、把發票 CSV 轉成報表、每天早上抓幾個網頁的資料……
# 不用大，重點是它對你有用。有用的東西你才會持續改它，才會真的學會。
#
# 而且記得：**先寫測試。**

# %%
print("🎉 全書完")
print()
print("📁 完整成品：examples/")
print("📖 附錄：docs/附錄A-速查表.md、附錄B-練習解答.md、附錄C-疑難排解.md")
