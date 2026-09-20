# 附錄 A：語法速查表

一頁帶走。找不到的請回該章查。

---

## 型別與變數

```python
品項 = "珍珠奶茶"     # str
單價 = 65            # int
折扣 = 0.9           # float
是會員 = True        # bool
備註 = None          # NoneType

type(單價)                    # <class 'int'>
isinstance(單價, int)         # True
str(65)  int("65")  float("65")  int(65.9)   # ⚠️ int() 直接砍小數

=   命名（賦值）
==  提問（比較）
```

**假值**：`False` `None` `0` `0.0` `""` `[]` `{}` `()` `set()` ← 空的、零的都是假

---

## 數字

```python
7 / 3      # 2.333  永遠 float
7 // 3     # 2      整除
7 % 3      # 1      餘數（判斷整除、算剩餘）
7 ** 3     # 343    次方
abs(-3)  max(a,b)  min(a,b)  sum(清單)  round(x, 2)

round(2.5)          # 2  ⚠️ 銀行家捨入
0.1 + 0.2 == 0.3    # False ⚠️ 浮點數
math.isclose(a, b)  # ✔ 正確的浮點數比較

# 台灣式四捨五入
from decimal import Decimal, ROUND_HALF_UP
int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

---

## 字串

```python
f"{品項} x{數量} = {單價*數量} 元"
f"{3.14159:.2f}"   # 3.14
f"{1234567:,}"     # 1,234,567
f"{0.9:.0%}"       # 90%
f"{'珍奶':<10}"     # 靠左   >靠右  ^置中
f"{7:03d}"         # 007
f"{單價=}"          # 單價=65   ← 除錯神器

.strip() .lstrip() .rstrip()
.split(",") .rsplit() .splitlines()
"、".join(清單)
.replace(舊, 新)
.lower() .upper() .title()
.startswith() .endswith()
.isdigit() .isalpha()
"x" in 字串
len(字串)
"-" * 30
repr(字串)          # 顯示出空白和 \n，除錯用

r"C:\temp\new"      # 原始字串（Windows 路徑）
"""多行字串"""
# ⚠️ 字串不可變，所有方法都是回傳新字串
```

---

## 判斷

```python
if 條件:
    ...
elif 其他條件:      # 命中一個就不再往下
    ...
else:
    ...

==  !=  >  >=  <  <=
in  not in
0 < x <= 100        # 連續比較
and  or  not        # ⚠️ 英文字，不是 && || !

x is None           # 跟 None/True/False 比較用 is
狀態 = "A" if 條件 else "B"     # 三元

match 值:           # Python 3.10+
    case "大杯": ...
    case _: ...
```

---

## 迴圈

```python
for 元素 in 清單: ...
for i in range(5): ...                    # 0~4，⚠️ 不含 5
for i, x in enumerate(清單, start=1): ...  # 編號 + 內容
for a, b in zip(清單A, 清單B): ...
for 鍵, 值 in 字典.items(): ...

while 條件: ...        # ⚠️ 記得讓條件有機會變成假
break      # 跳出整個迴圈
continue   # 跳過這一圈
for ... else:          # 沒 break 過才執行 else

# 累加器三步驟
總額 = 0              # 外面準備
for x in 清單:
    總額 += x         # 裡面更新
print(總額)           # 外面使用
```

---

## 資料結構

```python
# list 一串
[1, 2, 3]
清單[0] 清單[-1] 清單[1:3] 清單[::-1]
.append() .insert(i,x) .extend() .remove(值) .pop() .index(值) .count(值)
.sort()               # ⚠️ 就地排序，回傳 None
sorted(清單, key=..., reverse=True)      # 回傳新清單
[x*2 for x in 清單 if x > 1]             # 推導式
b = a.copy()          # ⚠️ b = a 不是複製！

# dict 查表
{"珍奶": 65}
表[鍵]  表.get(鍵, 預設)  表[鍵] = 值  del 表[鍵]
.keys() .values() .items() .pop() .update()
{k: v for k, v in ...}                   # 字典推導
鍵 in 表

# set 去重複
set(清單)  {1, 2}  set()   # ⚠️ 空集合不是 {}
A - B  A & B  A | B  A ^ B
.add() .discard() .remove()

# tuple 不可變
(1, 2)
a, b = 點                # 拆包
# 可以當字典的鍵

# 通用
len() sum() max() min() any() all() sorted() reversed()
```

---

## 函式

```python
def 名稱(必填, 選填=預設, *args, **kwargs) -> 回傳型別:
    """說明文件。"""
    return 結果

f(65, 45)              # 位置參數
f(name="珍奶")          # 關鍵字參數（布林參數一定要這樣寫）
def f(x, 清單=None):    # ⚠️ 絕對不要用 =[] 當預設值
    清單 = [] if 清單 is None else 清單

lambda x: x * 2        # 匿名函式（只用在 key= 這種地方）

# return vs print
return   # 把值交出去，可被計算、被測試 ← 邏輯用這個
print    # 顯示給人看 ← 最後一步
```

---

## 類別

```python
from dataclasses import dataclass, field

@dataclass                       # 自動產生 __init__ __repr__ __eq__
class Order:
    item: str
    quantity: int = 1
    toppings: list = field(default_factory=list)   # ⚠️ 不能寫 = []

    @property                    # 算出來的「特徵」，不用括號
    def total(self) -> int: ...

    def submit(self) -> None:    # 「動作」用方法
        ...

@dataclass(frozen=True)          # 唯讀，可當字典的鍵
@dataclass(order=True)           # 可排序

# 手寫版
class Order:
    def __init__(self, item): self.item = item
    def __repr__(self): ...      # 除錯顯示 ← 一定要寫
    def __str__(self): ...       # print 用
    def __eq__(self, other): ... # == 用 ← 測試需要它
    def __len__(self): ...

class 外送訂單(Order):            # 繼承（少用；先考慮組合）
    def total(self): return super().total + 50
```

---

## 例外

```python
try:
    危險的事()
except 特定錯誤 as e:
    處理(e)
except (錯誤A, 錯誤B):
    ...
else:
    沒出錯才做的
finally:
    一定會做的

raise ValueError(f"數量必須大於 0，收到 {n}")
raise 自訂錯誤("訊息") from 原本的錯誤

class 庫存不足(Exception): ...

# ⚠️ 三個禁忌
except:                 # 裸 except
except Exception: pass  # 吞掉例外
try: 包住整個函式        # 只包可能出錯的那幾行
```

**常見例外**：`ValueError` `TypeError` `KeyError` `IndexError` `AttributeError`
`FileNotFoundError` `ZeroDivisionError` `ImportError` `AssertionError`

---

## 檔案與路徑（跨平台）

```python
from pathlib import Path

p = Path("資料") / "2026-09-20.csv"      # ⚠️ 永遠這樣組路徑
p.name p.stem p.suffix p.parent p.parts
p.exists() p.is_file() p.is_dir() p.resolve()
Path("資料").mkdir(parents=True, exist_ok=True)
list(Path("資料").glob("*.csv"))         # rglob 遞迴
p.unlink(missing_ok=True)  Path("空目錄").rmdir()
shutil.rmtree(目錄)                      # 刪整棵

Path.cwd()                               # 執行位置（會變）
Path(__file__).resolve().parent          # 程式檔位置（固定）← 找資料用這個
Path.home()

p.write_text("內容", encoding="utf-8")    # ⚠️ 每次都寫 encoding
p.read_text(encoding="utf-8")
with open(p, "r", encoding="utf-8") as f:
    for 行 in f: ...                      # 大檔案逐行讀

# 模式：r 讀 / w ⚠️清空 / a 附加 / x 防覆蓋 / rb wb 二進位

# CSV
with open(p, "w", encoding="utf-8", newline="") as f:     # ⚠️ newline=""
    w = csv.DictWriter(f, fieldnames=[...]); w.writeheader(); w.writerows(rows)
with open(p, encoding="utf-8", newline="") as f:
    for 列 in csv.DictReader(f): int(列["金額"])           # ⚠️ 記得轉型
# 給 Excel 開：encoding="utf-8-sig"

# JSON
json.dump(物件, f, ensure_ascii=False, indent=2, sort_keys=True)
json.load(f)  json.dumps(物件)  json.loads(字串)
```

---

## 模組與套件

```python
import pricing
from pricing import price_of
from pricing import price_of as 查價
from pricing import *          # ❌ 絕對不要

if __name__ == "__main__":
    main()

# 找不到模組
cd 專案根目錄 && python3 -m 套件.模組
python3 -m pip install -e .
sys.path.insert(0, str(專案根目錄))     # Notebook 權宜之計，別寫死路徑

# import 順序：標準庫 / 第三方 / 自己的，各空一行
# ⚠️ 不要把檔案取名 random.py、json.py、test.py…
```

---

## 測試

```python
# assert（任何地方都能用）
assert 實際 == 預期, "失敗時的訊息"

# doctest（文件即測試）
def f(x):
    """
    >>> f(2)
    4
    """
import doctest; doctest.testmod()
python3 -m doctest 檔案.py -v

# unittest（標準庫，免安裝）
class TestX(unittest.TestCase):
    def setUp(self): ...
    def test_行為描述(self):
        self.assertEqual(實際, 預期)
        self.assertIn(a, b)  self.assertIsNone(x)  self.assertTrue(x)
        self.assertAlmostEqual(a, b)
        with self.assertRaises(ValueError): ...
        with self.subTest(x=x): ...          # 參數化
unittest.main(argv=[""], exit=False)          # Jupyter 裡這樣跑
python3 -m unittest -v                        # 終端機

# pytest（業界標準）
def test_行為描述():
    assert 實際 == 預期
with pytest.raises(ValueError, match="訊息"): ...
@pytest.fixture
def 資料(): return [...]
@pytest.mark.parametrize("a,b,expected", [(1,2,3), (2,3,5)])
def test_檔案(tmp_path): ...                  # 跨平台暫存目錄
pytest.importorskip("matplotlib")
@pytest.mark.skipif(條件, reason="...")

pytest -v / -x / -q / -k "關鍵字" / --lf

# 不用 pytest 也能測檔案
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "x.csv"
```

**TDD 三步驟**：🔴 寫會失敗的測試 → 🟢 寫剛好夠通過的程式 → 🔵 重構

**好測試準則**：AAA 結構、名稱描述行為、一個測試一件事、一定測邊界（空/零/剛好/剛好差一）、
不測第三方與內建、測試要快、每個 `raise` 配一個測試

---

## 標準函式庫常用

```python
# datetime
from datetime import date, datetime, timedelta
date.today()  今天.weekday()  今天.isoformat()  今天.strftime("%Y-%m-%d")
date.fromisoformat("2026-09-20")  datetime.strptime(s, "%Y/%m/%d")
今天 - timedelta(days=1)
# ⚠️ 把「今天」當參數傳進函式，否則無法測試

# collections
Counter(清單).most_common(3)
defaultdict(list)  defaultdict(int)
deque  namedtuple  OrderedDict

# statistics
mean() median() mode() stdev()       # ⚠️ 空清單會 StatisticsError

# re
re.sub(r"\D", "", 電話)   re.fullmatch(r"09\d{8}", 電話)
re.search()  re.findall()  re.match()
# \d \w \s . * + ? {n,m} ^ $ [abc] (...)
# ⚠️ 一律用 r"..."

# itertools
product() chain() islice() groupby()   # ⚠️ groupby 前要先 sorted

# random
random.Random(42)                      # 可重現的產生器 ← 測試用
randint() choice() sample() shuffle()

# 其他
math  decimal  pathlib  json  csv  os  sys  argparse
enum.Enum  functools.lru_cache  dataclasses  typing  sqlite3  zoneinfo
```

---

## 環境與套件

```bash
python3 --version                                # 🪟 py -3 --version
python3 -c "import sys; print(sys.executable)"   # 萬用診斷

python3 -m venv .venv          # 🪟 py -3 -m venv .venv
source .venv/bin/activate      # 🪟 .venv\Scripts\activate
deactivate

python3 -m pip install 套件     # ✔ 用 -m，保證裝對地方
pip install -r requirements.txt
pip install -e .               # 可編輯安裝
pip list / pip show / pip freeze

jupyter lab
python3 -m ipykernel install --user --name=專案名
```

```python
# Jupyter magic
%timeit 運算式    %time    %who    %reset -f
%load_ext autoreload
%autoreload 2
!{sys.executable} -m pip install 套件     # 在 Notebook 裡安裝，保證裝對
# ⚠️ !ls 不跨平台，改用 pathlib
```

---

## 跨平台檢查清單

| ❌ 不要 | ✅ 要 |
| --- | --- |
| `"資料/" + 檔名` | `Path("資料") / 檔名` |
| `"C:\\Users\\..."` | `Path(__file__).parent`、`Path.home()` |
| `open(p)` | `open(p, encoding="utf-8")` |
| `open(p, "w")` 寫 csv | `open(p, "w", newline="", encoding="utf-8")` |
| `/tmp/x.csv` | `tempfile` / pytest `tmp_path` |
| `date.today()` 寫死在函式裡 | 當成參數傳進去 |
| `strftime("%A")` | 自己做星期對照表 |
| `!ls` | `Path.iterdir()` |
| 假設檔名不分大小寫 | 一律當成有分（Linux 有分） |
| `python` | `python3` / 🪟 `py -3` |
