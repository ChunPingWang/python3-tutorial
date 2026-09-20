# %% [markdown]
# # 第 6 章：函式 —— 把做法包起來，只寫一次
#
# > 🎬 **情境**
# > 阿宏：「所有飲料調漲 5 元。」
# >
# > 你打開程式，發現「算價格」這件事你在三個地方各寫了一次：結帳畫面、日報表、會員 App。
# > 你改了兩處，漏了第三處。隔天阿宏發現 App 上的價格是舊的，客訴。

# %% [markdown]
# ## 6.1 😩 土法煉鋼：複製貼上邏輯

# %%
菜單 = {"珍珠奶茶": {"中杯": 55, "大杯": 65}}
品名, 杯型, 是會員 = "珍珠奶茶", "大杯", True

# 結帳畫面
價格 = 菜單[品名][杯型]
if 是會員:
    價格 = round(價格 * 0.9)
print("結帳畫面：", 價格)

# 日報表（一模一樣的三行）
價格 = 菜單[品名][杯型]
if 是會員:
    價格 = round(價格 * 0.9)
print("日報表  ：", 價格)

# 會員 App（這裡不小心打成 0.85，而且沒人發現）
價格 = 菜單[品名][杯型]
if 是會員:
    價格 = round(價格 * 0.85)
print("會員 App：", 價格, "← 對不起來了，但誰會發現？")

# %% [markdown]
# **重複的程式碼有三個致命傷：**
#
# 1. **改一個要改 N 個**，漏掉就是 bug
# 2. **複製時會抄錯**，而且錯得很難發現
# 3. **沒辦法測試** —— 你要怎麼寫 `assert` 去測「散落在三個檔案裡的六行」？
#
# > 🔍 **不能被測試的程式碼，通常是因為它沒有被好好地「包起來」。**
# > TDD 之所以讓程式結構變好，就是因為「想測試它」這個念頭會逼你把邏輯抽成
# > 一個有名字、有輸入、有輸出的東西 —— 那個東西就叫**函式**。

# %% [markdown]
# ## 6.2 🧪 先寫測試：測試先決定了函式的樣子

# %%
try:
    # 我希望怎麼「呼叫」它？
    assert price_of("珍珠奶茶", "大杯") == 65
    assert price_of("珍珠奶茶", "大杯", is_member=True) == 59
except NameError as 錯誤:
    print("🔴 紅燈：", 錯誤)

# %% [markdown]
# 光是寫這兩行，你就決定了：**函式名稱、參數順序、參數名稱、回傳型別**。
# 再多問一句「不存在的品項怎麼辦？」，你還決定了**錯誤處理策略**
# （我們決定讓它爆炸 —— 因為那代表點餐系統有 bug，不該默默算成 0 元）。
#
# > 🔍 **這就是 Test-Driven _Design_。**
# > 你先站在「使用者」的角度寫呼叫方式，再回頭實作。
# > 這樣寫出來的函式，介面幾乎一定比「先實作再想怎麼呼叫」好用。

# %% [markdown]
# ## 6.3 💡 定義函式

# %%
MENU = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
}


def price_of(name, size):
    """回傳指定品項與杯型的價格。"""      # docstring：說明文件
    return MENU[name][size]              # return：把結果送回去


print(price_of("珍珠奶茶", "大杯"))
print(price_of.__doc__)                  # docstring 可以被程式讀到

# %% [markdown]
# ### ⚠️ `return` 和 `print` 完全不同 —— 初學者最大的混淆點

# %%
def 版本A(a, b):
    print(a + b)          # 印在螢幕上，但沒把值交出來


def 版本B(a, b):
    return a + b          # 把值交出來


x = 版本A(1, 2)
y = 版本B(1, 2)
print(f"{x=}  ← 版本A 回傳 None")
print(f"{y=}  ← 版本B 回傳 3")

# %%
assert 版本B(1, 2) == 3          # ✔ 可以測試
try:
    assert 版本A(1, 2) == 3      # ✖ 回傳 None
except AssertionError:
    print("🔴 版本A 沒辦法測試，因為它什麼都沒回傳")

# %% [markdown]
# **判斷準則：如果你想對結果做任何事（計算、測試、存檔），就必須 `return`。**
# `print` 只是給人看的最後一步。
#
# > 🔍 這也是為什麼 TDD 會改善你的程式：
# > 只要你打算寫 `assert`，你自然會寫 `return` 而不是 `print`，
# > 而 `return` 版本的函式才能被組合、被重複使用。

# %% [markdown]
# ## 6.4 參數的各種形式

# %%
def 價格(name, size, is_member=False):
    p = MENU[name][size]
    return round(p * 0.9) if is_member else p


print(價格("珍珠奶茶", "大杯"))                    # 位置參數，順序重要
print(價格("珍珠奶茶", "大杯", True))              # 能動，但 True 是什麼意思？
print(價格("珍珠奶茶", "大杯", is_member=True))    # ✔ 清楚多了
print(價格(size="大杯", name="珍珠奶茶"))          # 用名字指定，順序不重要

# %% [markdown]
# ⚠️ **布林參數一定要用關鍵字寫法。** `f(x, True, False, True)` 三個月後沒人看得懂。

# %% [markdown]
# ### ⚠️⚠️ 絕對不要用可變物件當預設值

# %%
def 加訂單_錯誤版(訂單, 清單=[]):        # ✖ 災難
    清單.append(訂單)
    return 清單


print(加訂單_錯誤版("珍奶"))
print(加訂單_錯誤版("紅茶"), "← 為什麼上一次的還在？！")
print(加訂單_錯誤版("綠茶"), "← 越積越多")

# %% [markdown]
# **原因**：預設值只在「定義函式的那一刻」建立**一次**，之後每次呼叫都是**同一個清單**。

# %%
print("預設值的身分：", id(加訂單_錯誤版.__defaults__[0]), "← 永遠是同一個物件")


def 加訂單(訂單, 清單=None):            # ✔ 正確寫法
    if 清單 is None:
        清單 = []
    清單.append(訂單)
    return 清單


print(加訂單("珍奶"))
print(加訂單("紅茶"), "🟢 乾淨")

# %%
# *args / **kwargs：收集任意多個參數
def 總計(*金額們):
    return sum(金額們)


def 建立訂單(**欄位):
    return 欄位


print(總計(65, 45, 120))
print(建立訂單(品名="珍奶", 杯型="大杯"))

# %% [markdown]
# ## 6.5 型別註記：寫給人和工具看的說明

# %%
def price_of(name: str, size: str, is_member: bool = False) -> int:
    """回傳含折扣的價格（整數元）。"""
    p = MENU[name][size]
    return round(p * 0.9) if is_member else p


print(price_of.__annotations__)

# ⚠️ Python 不會檢查型別註記 —— 傳錯型別它照跑不誤
print("傳 list 進去也不會被擋，只是稍後會爆別的錯：")
try:
    price_of(["珍珠奶茶"], "大杯")
except TypeError as 錯誤:
    print("🔴", 錯誤)

# %% [markdown]
# 那為什麼要寫？
#
# 1. **給人看**：不用讀完整個函式就知道要傳什麼、拿到什麼
# 2. **給編輯器看**：VS Code 會自動補全、傳錯時畫紅線
# 3. **給檢查工具看**：`mypy`、`pyright` 可在執行前抓出型別錯誤
#
# ```python
# def f(x: int) -> str: ...
# def g(items: list[str]) -> dict[str, int]: ...
# def h(x: int | None) -> None: ...        # 可能是 int 也可能是 None（3.10+）
# ```
#
# > 🔍 **型別註記和測試是互補的**：註記說「應該是什麼型別」，測試說「應該是什麼值」。

# %% [markdown]
# ## 6.6 作用域：函式裡面和外面是兩個世界

# %%
稅率 = 0.05              # 全域變數


def 含稅(金額):
    結果 = 金額 * (1 + 稅率)      # ✔ 可以「讀」外面的變數
    return 結果


print(含稅(100))

try:
    print(結果)                   # ✖ 結果 只活在函式裡面
except NameError as 錯誤:
    print("🔴 NameError：", 錯誤)

# %%
# 經典錯誤：以為可以直接改外面的變數
計數 = 0


def 加一_錯誤版():
    計數 = 計數 + 1
    return 計數


try:
    加一_錯誤版()
except UnboundLocalError as 錯誤:
    print("🔴 UnboundLocalError：", 錯誤)
    print("   Python 看到函式裡有「計數 =」，就認定它是區域變數，")
    print("   於是右邊的 計數 變成「還沒賦值就使用」。")

# %%
# 解法不是 global，而是改用 return
def 加一(計數):
    return 計數 + 1


計數 = 0
計數 = 加一(計數)
計數 = 加一(計數)
print("🟢 計數 =", 計數, "（清楚、可測試）")

# %% [markdown]
# > ⚠️ **請把 `global` 當成最後手段。**
# > 用 `global` 的函式無法單獨測試（依賴外部狀態）、無法重複使用、debug 時你永遠不知道誰改了它。
# >
# > **好函式的定義：給它同樣的輸入永遠得到同樣的輸出，而且不偷偷改變外面的東西。**
# > 這種函式叫 *pure function*（純函式），也是最好測試的函式。

# %% [markdown]
# ## 6.7 🟢 讓測試變綠

# %%
from decimal import Decimal, ROUND_HALF_UP

MENU = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
}
MEMBER_DISCOUNT = 0.9


def round_half_up(value: float) -> int:
    """台灣習慣的四捨五入（逢五進一）。"""
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def price_of(name: str, size: str, is_member: bool = False) -> int:
    """回傳指定品項、杯型的價格；會員自動套用 9 折。

    品項或杯型不存在時拋出 KeyError —— 這代表點餐系統有 bug，
    不應該默默算成 0 元。
    """
    price = MENU[name][size]
    if is_member:
        price = round_half_up(price * MEMBER_DISCOUNT)
    return price


assert price_of("珍珠奶茶", "大杯") == 65
assert price_of("珍珠奶茶", "中杯") == 55
assert price_of("珍珠奶茶", "大杯", is_member=True) == 59
print("🟢 全綠")

# %%
# 「調漲 5 元」現在只要改一個地方
for 品項 in MENU:
    for 杯型 in MENU[品項]:
        MENU[品項][杯型] += 5

print("調漲後：", price_of("珍珠奶茶", "大杯"))
assert price_of("珍珠奶茶", "大杯") == 70
print("🟢 三個畫面同時更新，不會有人漏改")

# %% [markdown]
# ## 6.8 一個函式該做多少事？
#
# **一個函式只做一件事，而且名字要說得出它做了什麼。**
#
# 如果函式名字需要用「而且」「然後」來描述，它就該被拆開。

# %%
# ✖ 名字裡有「並」→ 做了兩件事，而且很難測（測試會在硬碟留檔案）
def 計算價格並存檔(品項, 數量, 單價):
    總額 = 單價 * 數量
    # open("報表.txt", "w").write(...)   ← 測試時這行很討厭
    return 總額


# ✔ 拆成兩個：一個純計算（好測），一個負責副作用（少量、集中）
def 計算總額(數量: int, 單價: int) -> int:
    return 數量 * 單價


def 存檔(內容: str, 路徑) -> None:
    ...


assert 計算總額(3, 65) == 195
print("🟢 三行測試搞定")

# %% [markdown]
# > 🔍 **好用的判斷法：這個函式好不好測試？**
# >
# > 「難測試」幾乎總是在告訴你「設計不好」。
# > **這是 TDD 送給你的免費設計警報器。**

# %% [markdown]
# ## 📌 本章速記

# %%
def 範例(必填: int, 選填: str = "預設") -> str:
    """說明文件。"""
    return f"{必填}{選填}"


assert 範例(1) == "1預設"
assert 範例(1, 選填="x") == "1x"
assert 範例.__doc__ == "說明文件。"


# 可變預設值陷阱
def 好(x, 清單=None):
    清單 = [] if 清單 is None else 清單
    清單.append(x)
    return 清單


assert 好(1) == [1] and 好(2) == [2]
print("🟢 速記通過")

# %% [markdown]
# ---
# ## 🧪 練習

# %% [markdown]
# ### 練習 6-1：把第 3 章的計價規則寫成函式
# 規則：員工價 40 一律優先；大杯 +10；會員 9 折（四捨五入）。

# %%
def calc_price(base, size, is_member, is_staff):
    pass  # 👉 你的實作


try:
    assert calc_price(65, "中杯", False, False) == 65
    assert calc_price(65, "大杯", False, False) == 75
    assert calc_price(65, "大杯", True, False) == 68
    assert calc_price(65, "大杯", True, True) == 40
    print("🟢 6-1 通過")
except AssertionError:
    print("🔴 還沒做或不正確")

# %% [markdown]
# ### 練習 6-2：找出 bug
# **先執行，看它怎麼死**，再想為什麼。

# %%
def 記錄訂單(品項, 紀錄=[]):
    紀錄.append(品項)
    return 紀錄


print(記錄訂單("珍奶"))
print(記錄訂單("紅茶"), "← 期望是 ['紅茶']")

try:
    assert 記錄訂單("綠茶") == ["綠茶"]
    print("🟢 6-2 通過")
except AssertionError:
    print("🔴 抓到了！提示：可變預設值陷阱，回去看 6.4 節")

# %% [markdown]
# ### 練習 6-3：寫一個「可測試」的函式
# 把下面這個難測的函式拆成兩個：一個算、一個印。

# %%
def 印出收據_難測(品項, 數量, 單價):
    總額 = 單價 * 數量
    print(f"{品項} x{數量} = {總額}")


# 👉 你的版本寫在這裡（讓下面的測試通過）


try:
    assert 計算總額2(3, 65) == 195
    print("🟢 6-3 通過")
except NameError:
    print("🔴 還沒做：請定義 計算總額2(數量, 單價)")

# %% [markdown]
# ---
# ➡️ 下一章：`07-測試驅動開發.ipynb` —— `assert` 寫到 40 個之後，你會想要更好的工具。
