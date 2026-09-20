# 附錄 B：練習解答

> ⚠️ **先自己寫過再看。** 看解答學到的東西，大約是自己卡住再解開的三分之一。
>
> 解答不只給程式碼，也說明**為什麼這樣寫**。很多題目有多種正確寫法。

---

## 第 1 章

### 1-1 記下第二筆訂單

```python
第二筆品項 = "冬瓜檸檬"
第二筆單價 = 45          # int，不是 "45"
第二筆數量 = 2
第二筆小計 = 第二筆單價 * 第二筆數量
```

⚠️ 測試裡的 `type(第二筆單價) is int` 就是在防「把價格存成字串」。
字串的 `"45" * 2` 會得到 `"4545"`，不是 90。

### 1-2 型別轉換

```python
小計答案 = int(數量文字) * int(單價文字)
```

⚠️ 忘記轉型的話 `"3" * "65"` 會直接 `TypeError`；
而 `"3" * 65` 更可怕 —— 它會給你一個 65 個 3 連在一起的字串，**不會報錯**。

### 1-3 找出三個錯誤

```python
冬瓜品項 = "冬瓜檸檬"      # 錯誤 1：忘了引號 → NameError
冬瓜數量 = 2              # 錯誤 2：數量是字串 "2"
冬瓜總價 = 45 * 冬瓜數量   # 錯誤 3：字串乘以數字會變成重複的字串
```

---

## 第 2 章

### 2-1 計算找零

```python
總額 = 65 * 3 + 45 * 2      # 285
找零 = 500 - 總額            # 215
```

### 2-2 提袋數量

```python
杯數, 一袋裝 = 197, 8
提袋數答案 = 杯數 // 一袋裝 + (1 if 杯數 % 一袋裝 else 0)    # 25
```

也可以用 `math.ceil(197 / 8)`，但整數運算比浮點數安全（不會有精度問題）。

### 2-3 清洗 LINE 訂單

```python
欄位 = [x.strip() for x in 髒資料.strip().split("|")]
乾淨品項 = 欄位[0]
乾淨價格 = int(欄位[2])
```

拆解：`.strip()` 去掉頭尾空白與換行 → `.split("|")` 切成三段 →
推導式對每一段再 `.strip()` → 價格轉 `int`。

### 2-4 對齊的一行

```python
行 = f"{報表品項:<12}{報表數量:>6,}{報表金額:>10,}"
```

`<12` 靠左寬 12、`>6,` 靠右寬 6 加千分位、`>10,` 靠右寬 10 加千分位。

---

## 第 3 章

### 3-1 飲料溫度建議

```python
def 建議(溫度):
    if 溫度 >= 30:
        return "冰的"
    elif 溫度 >= 20:
        return "常溫"
    return "熱的"
```

⚠️ **順序很重要**：`>= 30` 一定要寫在 `>= 20` 前面，否則 35 度會命中 `>= 20` 變成常溫。

### 3-2 滿額折扣

```python
def 折後金額(金額):
    if 金額 >= 500:
        return 金額 - 60
    elif 金額 >= 200:
        return 金額 - 20
    return 金額
```

### 3-3 找出 bug

原版把 `>= 200` 寫在 `>= 500` 前面，所以 500 元先命中 `>= 200`，只折了 20。

**修法**：把嚴格的條件放前面（同 3-2）。
**教訓**：多層 `elif` 一律**從最嚴格寫到最寬鬆**。這就是為什麼測試要包含 500 這個邊界。

---

## 第 4 章

### 4-1 只算會員的營收

```python
def 會員營收(訂單):
    總額 = 0
    for 筆 in 訂單:
        if 筆["會員"]:
            總額 += 筆["金額"]
    return 總額

# 或一行
def 會員營收(訂單):
    return sum(筆["金額"] for 筆 in 訂單 if 筆["會員"])
```

### 4-2 九九乘法表的某一行

```python
def 乘法表行(n):
    return " ".join(f"{n}x{i}={n * i}" for i in range(1, 10))
```

用 `join` 而不是一直 `+=` 字串：字串不可變，每次 `+=` 都會造一個新字串，資料多時很慢。

### 4-3 第一筆大額訂單的序號

```python
def 第一筆大額(訂單):
    for 序號, 金額 in enumerate(訂單, start=1):
        if 金額 > 100:
            return 序號
    return None
```

`return` 會直接跳出整個迴圈，比 `break` + 旗標乾淨。
⚠️ 最後那行 `return None` 可以省略（函式預設回傳 `None`），但**寫出來比較清楚**。

### 4-4 抓 bug

`總額 = 0` 寫在迴圈**裡面**，所以每一圈都歸零，最後只剩下最後一筆。

**修法**：把 `總額 = 0` 移到迴圈外面。
**教訓**：累加器三步驟 —— 外面準備、裡面更新、外面使用。

---

## 第 5 章

### 5-1 庫存管理

```python
def 需要補貨(庫存):
    return [品項 for 品項, 數量 in 庫存.items() if 數量 < 10]
```

### 5-2 每個品項的營收

```python
def 品項營收(訂單):
    結果 = {}
    for 品項, 金額 in 訂單:
        結果[品項] = 結果.get(品項, 0) + 金額      # .get 預設值的經典用法
    return 結果

# 或用 defaultdict（第 12 章）
from collections import defaultdict
def 品項營收(訂單):
    結果 = defaultdict(int)
    for 品項, 金額 in 訂單:
        結果[品項] += 金額
    return dict(結果)
```

### 5-3 滯銷品

```python
def 滯銷品(全部, 賣出):
    return set(全部) - set(賣出)
```

集合差集一行解決，不用寫迴圈。

### 5-4 預測輸出

```
a = [1, 2, 3, 4]      ← b 是 a 的別名，append(4) 也改到 a
b = [1, 2, 3, 4]      ← 和 a 是同一個清單
c = [1, 2, 3, 5]      ← copy() 出來的獨立清單
```

**教訓**：`b = a` 不是複製。要複製用 `a.copy()`、`a[:]` 或 `list(a)`。

---

## 第 6 章

### 6-1 計價函式

```python
def calc_price(base, size, is_member, is_staff):
    if is_staff:                       # guard clause：員工價優先，直接回傳
        return 40
    price = base + (10 if size == "大杯" else 0)
    if is_member:
        price = round_half_up(price * 0.9)
    return price
```

### 6-2 可變預設值陷阱

預設值 `[]` 只在「定義函式那一刻」建立**一次**，之後每次呼叫都是同一個清單。

```python
def 記錄訂單(品項, 紀錄=None):
    紀錄 = [] if 紀錄 is None else 紀錄
    紀錄.append(品項)
    return 紀錄
```

### 6-3 可測試的函式

```python
def 計算總額2(數量: int, 單價: int) -> int:     # 純函式，好測
    return 數量 * 單價

def 印出收據(品項, 數量, 單價) -> None:          # 只負責顯示
    print(f"{品項} x{數量} = {計算總額2(數量, 單價)}")
```

**教訓**：把「計算」和「顯示」分開，計算的部分才測得動。

---

## 第 7 章

### 7-1 用 TDD 做提袋數量

```python
def 袋子數(杯數):
    if 杯數 <= 0:
        return 0
    return (杯數 + 5) // 6          # 等同 ceil(杯數 / 6)
```

`(n + k - 1) // k` 是「無條件進位的整數除法」慣用寫法，不用浮點數。

⚠️ `test_零杯不需要袋子` 是最容易被忘記的測試，
而「0 杯給 1 個袋子」在真實世界就是一張空的出貨單。

### 7-2 補完 doctest

```python
>>> 折扣後金額(100, 0.9)
90
>>> 折扣後金額(65, 0.9)
59
```

⚠️ 如果用內建 `round`，`round(58.5)` 會是 58，doctest 會失敗 —— 這正是它的價值。

### 7-3 這個測試有什麼問題

1. **失敗就中斷**：第二行失敗，第三、四行根本不會執行
2. **名稱沒有意義**：`test_全部` 說不出它在測什麼
3. **一個測試驗證四件事**：失敗時不知道是哪件壞了

**修法**：拆成四個有描述性名稱的測試，或用參數化。

### 7-4 找出遺漏的測試

少了 **空清單** 的測試：

```python
def test_空訂單的平均是零():
    assert 平均客單價([]) == 0
```

原本的函式會 `ZeroDivisionError`。修法：

```python
def 平均客單價(訂單):
    if not 訂單:
        return 0
    return sum(訂單) / len(訂單)
```

**打烊時一筆訂單都沒有是很正常的事**（週一公休、颱風天），日報表不該因此掛掉。

---

## 第 8 章

### 8-1 動手拆檔

```
mytools/
├── __init__.py
├── pricing.py      round_half_up, price_of, 結帳
└── stats.py        總營收, 平均客單價, 熱銷品項
tests/
├── test_pricing.py
└── test_stats.py
```

在**專案根目錄**執行 `pytest`（或 `python3 -m unittest discover`）。
出現 `ModuleNotFoundError` 的話，加一個 `conftest.py`（見 `examples/conftest.py`）
或 `pip install -e .`。

### 8-2 預測 `__name__`

```
a 的 __name__ 是 a            ← a 被 import，所以是模組名
b 的 __name__ 是 __main__     ← b 是直接執行的那個
```

### 8-3 找出問題

`import json` 會匯入**小美自己的 `json.py`**，而不是標準庫，
因為「腳本所在目錄」在 `sys.path` 的最前面。

症狀通常是 `AttributeError: module 'json' has no attribute 'load'` 這種很難懂的錯誤。

**修法**：把檔案改名（例如 `my_json.py`），並刪掉 `__pycache__/json.*.pyc`。

---

## 第 9 章

### 9-1 round-trip 測試

完整答案見 `examples/drinkshop/storage.py` 與 `examples/tests/test_storage.py`。重點：

```python
def 存訂單(訂單, 路徑):
    路徑 = Path(路徑)
    路徑.parent.mkdir(parents=True, exist_ok=True)
    with 路徑.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["品項", "金額"])
        w.writeheader()
        w.writerows(訂單)

def 讀訂單(路徑):
    with Path(路徑).open(encoding="utf-8", newline="") as f:
        return [{"品項": r["品項"], "金額": int(r["金額"])} for r in csv.DictReader(f)]
                                              # ↑ 一定要轉型
```

### 9-2 找出跨平台問題

```python
with open("C:\\reports\\" + str(date.today()) + ".csv", "w") as f:
```

**五個問題：**

1. 寫死 Windows 絕對路徑 → 用 `Path(__file__).parent / "reports"`
2. 字串拼接路徑 → 用 `/` 運算子
3. 沒有 `encoding="utf-8"` → Windows 上中文會壞
4. 寫 CSV 沒有 `newline=""` → Windows 上多空行
5. 資料夾不存在會爆 → `mkdir(parents=True, exist_ok=True)`

```python
def 存日報表(資料, 今天: date, 資料夾: Path):
    資料夾.mkdir(parents=True, exist_ok=True)
    路徑 = 資料夾 / f"{今天.isoformat()}.csv"
    路徑.write_text(資料, encoding="utf-8")
    return 路徑
```

（順便把 `date.today()` 變成參數 —— 第 12 章的原則。）

### 9-3 把難測的函式拆開

```python
def 統計(訂單) -> str:                      # 純函式
    if not 訂單:
        return "總額 0 平均 0.0"            # 邊界
    總額 = sum(o["金額"] for o in 訂單)
    return f"總額 {總額} 平均 {總額 / len(訂單):.1f}"

def 存檔(內容: str, 路徑: Path) -> None:
    Path(路徑).write_text(內容, encoding="utf-8")

# 測試（不碰硬碟）
assert 統計([{"金額": 100}, {"金額": 200}]) == "總額 300 平均 150.0"
assert 統計([{"金額": 100}]) == "總額 100 平均 100.0"
assert 統計([]) == "總額 0 平均 0.0"
```

---

## 第 10 章

### 10-1 / 10-2 Member

```python
from dataclasses import dataclass

@dataclass
class Member:
    姓名: str
    電話: str
    累積消費: int = 0

    @property
    def 等級(self) -> str:
        if self.累積消費 >= 5000:
            return "金卡"
        if self.累積消費 >= 1000:
            return "銀卡"
        return "一般"
```

10-2 自動通過，因為 `@dataclass` 送你 `__eq__`。
手寫版要多寫 `__init__`、`__repr__`、`__eq__` 三個方法共十幾行。

### 10-3 購物車的問題

`def __init__(self, 商品=[])` 是可變預設值陷阱：所有購物車共用同一個清單。

```python
@dataclass
class 購物車:
    商品: list = field(default_factory=list)
```

或手寫版 `商品=None` 再在 `__init__` 裡建立新清單。

### 10-4 該用類別嗎

| | 答案 | 理由 |
| --- | --- | --- |
| (a) 攝氏轉華氏 | **函式** | 沒有狀態 |
| (b) 會員 | **類別** | 有資料 + 針對該資料的行為 |
| (c) 字串工具 | **模組** | 一堆無狀態函式，用模組整理就好 |
| (d) 購物車 | **類別** | 有狀態（商品清單）+ 操作它的行為 |

**判斷法**：沒有 `self.xxx`（沒有狀態）的類別，就不該是類別。

---

## 第 11 章

### 11-1 安全的平均

```python
def 安全平均(訂單):
    if not 訂單:
        return 0
    return sum(訂單) / len(訂單)
```

用 `if not 訂單` 而不是 `try/except ZeroDivisionError`：
**空清單是正常情況，不是例外情況。**

### 11-2 自訂例外

```python
def 扣庫存(庫存: dict, 品項: str, 數量: int) -> dict:
    if 品項 not in MENU:
        raise 品項不存在(f"菜單上沒有 {品項}")
    剩餘 = 庫存.get(品項, 0)
    if 剩餘 < 數量:
        raise 庫存不足(f"{品項} 只剩 {剩餘} 杯，你要 {數量} 杯")
    return {**庫存, 品項: 剩餘 - 數量}       # 回傳新字典，不改動參數
```

完整版見 `examples/drinkshop/orders.py` 的 `deduct_stock`。

### 11-3 三個問題

```python
def 讀設定(路徑):
    try:
        with open(路徑) as f:        # 問題 2：沒有 encoding="utf-8"
            return json.load(f)
    except:                          # 問題 1：裸 except，連 Ctrl+C 都接住
        return {}                    # 問題 3：吞掉例外，永遠不知道出了什麼事
```

```python
def 讀設定(路徑) -> dict:
    try:
        with open(路徑, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.info("設定檔不存在，使用預設值：%s", 路徑)
        return {}
    except json.JSONDecodeError as 錯誤:
        raise ValueError(f"設定檔格式錯誤：{路徑}") from 錯誤
```

注意兩種錯誤的**處理方式不同**：檔案不存在是正常的（用預設值），
但檔案格式壞掉是需要人處理的問題（拋出去）。

### 11-4 讀 traceback

- **錯誤是什麼**：`ZeroDivisionError: division by zero`
- **在哪一行**：`report.py` 第 7 行，`日報表` 函式裡的 `總額 / len(訂單)`
- **怎麼走到那裡**：`<module>` 第 12 行呼叫 `日報表(今日訂單)`
- **根本原因**：`今日訂單` 是空的 → 少了空清單的邊界處理

---

## 第 12 章

### 12-1 日期計算

```python
def 第幾天(某天: date) -> int:
    return 某天.day

def 上週同一天(某天: date) -> date:
    return 某天 - timedelta(weeks=1)
```

`timedelta` 自動處理跨月、跨年、閏年，不要自己算。

### 12-2 銷售排行榜

```python
from collections import Counter

def 排行榜(訂單, 前幾名):
    return Counter(訂單).most_common(前幾名)
```

### 12-3 清洗電話

```python
import re

def 清洗電話(原始: str) -> str:
    數字 = re.sub(r"\D", "", 原始)
    if 數字.startswith("886"):
        數字 = "0" + 數字[3:]
    return 數字
```

### 12-4 把不可測的函式改成可測的

```python
def 今日優惠(某天: date) -> float:
    return 0.8 if 某天.weekday() == 2 else 1.0

# 測試
assert 今日優惠(date(2026, 9, 23)) == 0.8      # 週三
assert 今日優惠(date(2026, 9, 21)) == 1.0      # 週一
```

呼叫端寫 `今日優惠(date.today())`。
**不可控的東西（時間、亂數、檔案）一律變成參數** —— 這是全書最實用的一條設計原則。

---

## 第 13、14 章

這兩章的練習都是開放式的專案練習，完整參考實作在 [`examples/`](../examples/)：

- **13 章**：`pyproject.toml` 的 `optional-dependencies`、`drinkshop/report.py` 的 `text_bar_chart`
  （不需要 matplotlib 的繪圖）
- **14 章**：整個 `drinkshop` 套件 + 75 個測試

第 14 章練習 3（把 `MEMBER_THRESHOLD` 改成 300）的預期答案：
會有 **`test_剛好達到門檻就打折`** 和 **`test_會員滿門檻才打折`** 等幾個測試變紅，
而且**剛好就是**你該一起修改的那幾個。這就是測試作為「規格書」的價值。
