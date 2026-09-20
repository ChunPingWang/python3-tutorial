# %% [markdown]
# # 第 10 章：類別與物件 —— 把資料和行為綁在一起
#
# > 🎬 **情境**
# > 阿宏的訂單越來越複雜：品項、杯型、甜度、冰塊、加料、數量、會員、備註。
# >
# > ```python
# > def 結帳(品項, 杯型, 甜度, 冰塊, 加料, 數量, 是會員, 備註): ...
# > ```
# >
# > 小美呼叫時寫成 `結帳("珍奶", "大杯", "半糖", "少冰", None, 2, True, "")` ——
# > 她把甜度和冰塊寫反了，程式照跑，客人拿到全糖去冰。

# %% [markdown]
# ## 10.1 😩 土法煉鋼：參數地獄

# %%
MENU = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
}

# 用字典？好一點，但沒有任何保護
訂單字典 = {"品項": "珍珠奶茶", "杯形": "大杯"}      # ← 打錯字「杯形」，程式不報錯

print("有哪些欄位？", list(訂單字典))
try:
    訂單字典["杯型"]
except KeyError as 錯誤:
    print("🔴 KeyError：", 錯誤, "← 三小時後在另一個檔案才爆出來")

# %% [markdown]
# 字典的問題：
#
# 1. **打錯欄位名不會報錯**，等到取用時才爆
# 2. **不知道有哪些欄位**，編輯器無法自動補全
# 3. **資料和行為分開**：算價格的函式在別的地方，你得自己記得要呼叫它

# %% [markdown]
# ## 10.2 🧪 先寫測試：我希望怎麼用它？

# %%
try:
    訂單 = Order(品項="珍珠奶茶", 杯型="大杯", 數量=2, 是會員=True)
    assert 訂單.小計 == 130
except NameError as 錯誤:
    print("🔴 紅燈：", 錯誤)

# %% [markdown]
# 我希望的樣子：
#
# ```python
# assert 訂單.品項 == "珍珠奶茶"
# assert 訂單.單價 == 65             # 自己知道去查菜單
# assert 訂單.小計 == 130            # 自己會算
# assert 訂單.應付 == 117            # 自己知道會員打折
# assert "珍珠奶茶 x2" in str(訂單)   # 自己知道怎麼印出來
# ```
#
# 看出差別了嗎？**資料不再是死的**。訂單自己知道怎麼算價格、怎麼呈現自己。
#
# 這就是物件導向的核心：**把「資料」和「處理這份資料的行為」放在一起。**

# %% [markdown]
# ## 10.3 💡 class 基礎

# %%
class Order:
    """一筆訂單。"""

    def __init__(self, 品項, 杯型="中杯", 數量=1, 是會員=False):
        self.品項 = 品項              # self.xxx = 這個物件自己的資料（屬性）
        self.杯型 = 杯型
        self.數量 = 數量
        self.是會員 = 是會員

    def 小計(self):                   # 方法：這個物件會做的事
        return MENU[self.品項][self.杯型] * self.數量


訂單 = Order("珍珠奶茶", "大杯", 數量=2)     # 建立一個物件（實例）
print(訂單.品項)          # 讀屬性
print(訂單.小計())        # 呼叫方法

# %% [markdown]
# | 名詞 | 意思 | 類比 |
# | --- | --- | --- |
# | **類別 class** | 藍圖、模子 | 「訂單」這個概念 |
# | **實例 instance** | 用藍圖做出來的東西 | 阿宏今天的第 37 筆訂單 |
# | **屬性 attribute** | 物件的資料 | 這筆訂單的品項是珍奶 |
# | **方法 method** | 物件會做的事 | 這筆訂單算得出小計 |

# %% [markdown]
# ### `self` 是什麼？
#
# **`self` 就是「這個物件自己」。**

# %%
print("你這樣寫    ：", 訂單.小計())
print("Python 這樣跑：", Order.小計(訂單), "← self 就是 訂單")

# %% [markdown]
# 三條規則：
#
# 1. **每個方法的第一個參數都要寫 `self`**
# 2. **呼叫時不用傳 `self`**，Python 自動帶入
# 3. **要存取自己的屬性一定要加 `self.`**

# %%
class 錯誤示範:
    def __init__(self, 數量):
        self.數量 = 數量

    def 小計(self):
        return 數量 * 65          # ✖ 忘了 self.


try:
    錯誤示範(2).小計()
except NameError as 錯誤:
    print("🔴 NameError：", 錯誤, "← 忘了寫 self.")

# %% [markdown]
# ## 10.4 特殊方法（dunder methods）
#
# 名字前後有兩個底線的方法叫 dunder（double underscore），它們讓你的類別融入 Python 的語法。

# %%
# 先看沒定義 dunder 的下場
class 陽春訂單:
    def __init__(self, 品項):
        self.品項 = 品項


a = 陽春訂單("珍珠奶茶")
b = 陽春訂單("珍珠奶茶")
print("print 出來：", a, "← 完全看不出是什麼")
print("內容相同的兩筆相等嗎？", a == b, "← 竟然是 False！")

# %%
class Order:
    def __init__(self, 品項, 數量=1):
        self.品項 = 品項
        self.數量 = 數量

    def __repr__(self):                      # 除錯顯示 ← 一定要寫
        return f"Order(品項={self.品項!r}, 數量={self.數量})"

    def __str__(self):                       # print() 用，給人看的版本
        return f"{self.品項} x{self.數量}"

    def __eq__(self, other):                 # == 用 ← 測試需要它
        return (self.品項, self.數量) == (other.品項, other.數量)

    def __len__(self):                       # len() 用
        return self.數量


訂單 = Order("珍珠奶茶", 2)
print("print（用 __str__）：", 訂單)
print("repr （用 __repr__）：", repr(訂單))
print("相等（用 __eq__）  ：", Order("珍珠奶茶", 2) == Order("珍珠奶茶", 2))
print("長度（用 __len__） ：", len(訂單))

# %% [markdown]
# > 🔍 **`__eq__` 和測試的關係**
# >
# > 沒有 `__eq__` 時，`assert 訂單A == 訂單B` 比較的是「是不是同一個記憶體位址」，永遠 `False`。
# > 你只好寫成：
# >
# > ```python
# > assert 訂單A.品項 == 訂單B.品項
# > assert 訂單A.數量 == 訂單B.數量      # 有 8 個欄位就寫 8 行
# > ```
# >
# > 定義了 `__eq__`，一行就搞定。**「好不好測試」再一次告訴你該怎麼設計。**

# %% [markdown]
# ## 10.5 💡 dataclass：少寫 80% 的樣板

# %%
from dataclasses import dataclass, field


@dataclass
class Order:
    品項: str
    杯型: str = "中杯"
    數量: int = 1
    是會員: bool = False
    加料: list[str] = field(default_factory=list)    # ⚠️ 可變預設值要這樣寫！

    def 小計(self) -> int:
        return MENU[self.品項][self.杯型] * self.數量


訂單 = Order("珍珠奶茶", "大杯", 數量=2)
print(訂單)                                        # __repr__ 自動產生
print(訂單 == Order("珍珠奶茶", "大杯", 數量=2))     # __eq__ 自動產生
print(訂單.小計())

# %% [markdown]
# `@dataclass` 自動幫你產生 `__init__`、`__repr__`、`__eq__`。
# 上面那 4 個欄位如果手寫，光 `__init__` 就 5 行，`__repr__` 和 `__eq__` 再 6 行。

# %%
# ⚠️ 可變預設值的陷阱又來了（第 6 章）
@dataclass
class 危險購物車:
    商品: list = field(default_factory=list)


# 正確版：每個實例有自己的清單
車1, 車2 = 危險購物車(), 危險購物車()
車1.商品.append("珍奶")
print("用 default_factory：", 車1.商品, 車2.商品, "🟢 互不影響")

# 如果寫成 商品: list = [] —— dataclass 會直接拒絕你，這是好事
try:
    @dataclass
    class 真的危險:
        商品: list = []
except ValueError as 錯誤:
    print("🔴 dataclass 直接擋下：", 錯誤)

# %% [markdown]
# ### 常用選項
#
# ```python
# @dataclass(frozen=True)     # 唯讀，建立後不能改 → 可以當字典的鍵
# @dataclass(order=True)      # 自動產生 <、> 等比較方法，可以排序
# @dataclass(slots=True)      # 省記憶體（3.10+）
# ```

# %%
@dataclass(frozen=True)
class 座標:
    x: int
    y: int


點 = 座標(1, 2)
print("frozen 的好處：可以當字典的鍵 →", {點: "門市A"})

try:
    點.x = 5
except Exception as 錯誤:
    print("🔴", type(錯誤).__name__, "：", 錯誤, "← 唯讀")

# %% [markdown]
# > 🔍 **建議：資料為主的類別一律用 `dataclass`。**
# > 只有需要複雜初始化邏輯時才手寫 `__init__`。
# > **少寫的每一行樣板，都是少一個出錯的機會。**

# %% [markdown]
# ## 10.6 屬性 vs 方法：@property

# %%
from decimal import Decimal, ROUND_HALF_UP


def round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class Order:
    品項: str
    杯型: str = "中杯"
    數量: int = 1
    是會員: bool = False

    @property
    def 單價(self) -> int:
        return MENU[self.品項][self.杯型]

    @property
    def 小計(self) -> int:
        return self.單價 * self.數量

    @property
    def 應付(self) -> int:
        return round_half_up(self.小計 * 0.9) if self.是會員 else self.小計

    def __str__(self) -> str:
        return f"{self.品項} x{self.數量} = {self.應付} 元"


訂單 = Order("珍珠奶茶", "大杯", 數量=2, 是會員=True)
print("單價：", 訂單.單價, "（不用括號！）")
print("小計：", 訂單.小計)
print("應付：", 訂單.應付)
print(訂單)

# %%
# @property 是「即時計算」的，改了數量它自動跟著變
訂單.數量 = 3
print("改成 3 杯後，小計自動變成：", 訂單.小計)

# %% [markdown]
# **什麼時候用 `@property`？**
#
# | 用 property | 用方法 |
# | --- | --- |
# | 很快（幾乎瞬間） | 要花時間（查資料庫、打 API） |
# | 沒有副作用 | 會改變東西 |
# | 概念上是「特徵」 | 概念上是「動作」 |
#
# `訂單.小計` 讀起來像特徵 ✔；`訂單.送出訂單()` 是動作，一定要用方法。

# %% [markdown]
# ## 10.7 繼承：什麼時候該用（以及大多數時候不該用）

# %%
@dataclass
class 外送訂單(Order):               # 繼承 Order 的所有東西
    外送費: int = 50

    @property
    def 應付(self) -> int:
        return super().應付 + self.外送費      # super() = 「父類別的版本」


一般 = Order("珍珠奶茶", "大杯", 數量=2)
外送 = 外送訂單("珍珠奶茶", "大杯", 數量=2)

print("一般訂單應付：", 一般.應付)
print("外送訂單應付：", 外送.應付, "← 小計是繼承來的，應付是自己覆寫的")
print("外送訂單也有小計：", 外送.小計)
print("外送訂單是一種訂單嗎？", isinstance(外送, Order))

# %% [markdown]
# > ⚠️ **初學者最常見的錯誤：濫用繼承。**
# >
# > 繼承的正確條件是「**B 是一種 A**」（外送訂單**是一種**訂單 ✔）。
# > 不是「B 需要用到 A 的功能」—— 那應該用**組合**：
# >
# > ```python
# > # ✖ 錯：訂單不「是一種」印表機
# > class Order(印表機): ...
# >
# > # ✔ 對：訂單「有一個」印表機
# > @dataclass
# > class Order:
# >     印表機: 印表機
# > ```
# >
# > **實務準則：先用組合，真的出現「是一種」關係時才用繼承。**
# > 深層繼承（超過兩層）幾乎總是設計失誤的訊號。

# %% [markdown]
# ## 10.8 🧪 測試類別

# %%
def test_一般訂單的小計():
    訂單 = Order("珍珠奶茶", "大杯", 數量=2)
    assert 訂單.小計 == 130


def test_會員訂單自動打九折():
    訂單 = Order("珍珠奶茶", "大杯", 數量=2, 是會員=True)
    assert 訂單.應付 == 117


def test_內容相同的兩筆訂單相等():
    assert Order("珍珠奶茶") == Order("珍珠奶茶")        # 靠 dataclass 的 __eq__


def test_修改數量後小計自動更新():
    訂單 = Order("珍珠奶茶", "大杯")
    訂單.數量 = 3
    assert 訂單.小計 == 195                              # 靠 @property


def test_外送訂單要加外送費():
    assert 外送訂單("珍珠奶茶", "大杯", 數量=2).應付 == 180


for 測試 in [test_一般訂單的小計, test_會員訂單自動打九折, test_內容相同的兩筆訂單相等,
            test_修改數量後小計自動更新, test_外送訂單要加外送費]:
    測試()
    print("🟢", 測試.__name__)

# %% [markdown]
# ### 測試類別的三個要點
#
# 1. **每個測試自己建立物件**，不要共用（共用會讓測試互相影響）
# 2. **測「行為」，不要測「內部實作」**
#    ```python
#    assert 訂單.應付 == 117         # ✔ 測行為
#    assert 訂單._快取價格 == 130     # ✖ 測內部，一重構就壞
#    ```
# 3. **`__eq__` 讓斷言變一行**
#
# > 🔍 測試應該像「使用者」一樣使用你的類別。
# > 如果測試需要偷看內部，代表你要嘛測錯東西，要嘛公開介面設計得不夠好。

# %% [markdown]
# ## 10.9 什麼時候**不**需要類別
#
# 初學者學會 class 之後很容易什麼都做成類別。**不要。**
#
# | 情況 | 用什麼 |
# | --- | --- |
# | 只有資料，沒有行為 | `dataclass` 或字典 |
# | 只有行為，沒有狀態 | **函式就好** |
# | 一堆函式想「整理在一起」 | **模組**（第 8 章），不是類別 |
# | 資料 + 針對該資料的行為 | ✔ 類別 |

# %%
# ✖ 不必要的類別
class 計算機:
    def 加(self, a, b):
        return a + b


# ✔ 函式就好
def 加(a, b):
    return a + b


print(計算機().加(1, 2), 加(1, 2), "← 結果一樣，但右邊少了一層沒意義的包裝")
print("\n判斷法：如果你的類別沒有任何 self.xxx（沒有狀態），它就不該是類別。")

# %% [markdown]
# ## 📌 本章速記

# %%
@dataclass
class 速記範例:
    必填: str
    有預設: int = 1
    可變預設: list = field(default_factory=list)      # ⚠️ 不能寫 = []

    @property
    def 算出來的特徵(self) -> int:                     # 不用括號
        return self.有預設 * 2

    def 做一個動作(self) -> None:                      # 動作用方法
        pass


x = 速記範例("a")
assert x.算出來的特徵 == 2
assert 速記範例("a") == 速記範例("a")                  # dataclass 送你 __eq__
assert repr(速記範例("a")).startswith("速記範例(")      # 也送你 __repr__
print("🟢 速記通過")

# %% [markdown]
# ---
# ## 🧪 練習

# %% [markdown]
# ### 練習 10-1：用 dataclass 做一個 Member
# 欄位：`姓名`(str)、`電話`(str)、`累積消費`(int，預設 0)
# 屬性：`等級` → 累積消費 >= 5000 是「金卡」、>= 1000 是「銀卡」、否則「一般」

# %%
# 👉 你的 Member 寫在這裡


try:
    assert Member("小美", "0912345678").等級 == "一般"
    assert Member("小美", "0912345678", 累積消費=1000).等級 == "銀卡"
    assert Member("小美", "0912345678", 累積消費=4999).等級 == "銀卡"
    assert Member("小美", "0912345678", 累積消費=5000).等級 == "金卡"
    print("🟢 10-1 通過")
except NameError as 錯誤:
    print("🔴 還沒做：", 錯誤)

# %% [markdown]
# ### 練習 10-2：讓兩個內容相同的 Member 相等

# %%
try:
    assert Member("小美", "0912") == Member("小美", "0912")
    print("🟢 10-2 通過（用 dataclass 的話這題自動通過）")
    print("   試著用手寫 class 做一次，體會 dataclass 幫你省了多少。")
except NameError:
    print("🔴 請先完成 10-1")

# %% [markdown]
# ### 練習 10-3：這段程式有什麼問題？
#
# ```python
# class 購物車:
#     def __init__(self, 商品=[]):      # ← 這行
#         self.商品 = 商品
# ```
#
# **先想，再執行下一格。**

# %%
class 購物車:
    def __init__(self, 商品=[]):
        self.商品 = 商品


車1 = 購物車()
車2 = 購物車()
車1.商品.append("珍奶")

print("車1：", 車1.商品)
print("車2：", 車2.商品, "← 車2 根本沒加東西！")
print("\n👉 為什麼？回去看第 6 章的「可變預設值陷阱」。")
print("   正確寫法：商品=None，然後在 __init__ 裡 self.商品 = [] if 商品 is None else 商品")
print("   或者直接用 @dataclass + field(default_factory=list)")

# %% [markdown]
# ### 練習 10-4：該用類別嗎？
#
# 下面哪些應該做成類別，哪些應該是函式或模組？
#
# - (a) 把攝氏轉華氏
# - (b) 一個會員，有姓名、消費紀錄、可以計算等級
# - (c) 一組字串處理工具：去空白、轉半形、移除標點
# - (d) 一個購物車，可以加商品、移除商品、算總價
#
# （答案在附錄 B）

# %% [markdown]
# ---
# ➡️ 下一章：`11-例外與除錯.ipynb` —— 客人輸入「兩杯」而不是「2」，你的程式直接死掉。
