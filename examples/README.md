# `drinkshop` —— 教材的綜合範例專案

這是第 14 章用 TDD 一步步做出來的成品，也是第 8、9 章「拆檔案」「跨平台 I/O」的完整示範。

**核心功能一個第三方套件都不需要**，只用 Python 標準函式庫。

---

## 快速開始

```bash
cd examples

# 1. 確認環境
python3 hello.py          # 🍎🐧
py -3 hello.py            # 🪟

# 2. 跑測試（不需要安裝任何東西）
python3 run_tests.py

# 3. 跑測試（有裝 pytest 的話，報表更漂亮）
pip install pytest
pytest

# 4. 試玩
python3 -m drinkshop.cli demo                  # 產生示範訂單並印出日報表
python3 -m drinkshop.cli seed 資料 --days 7     # 產生 7 天的示範資料
python3 -m drinkshop.cli report 資料            # 讀資料夾產生月報
```

---

## 專案結構

```
examples/
├── pyproject.toml          專案設定（依賴、pytest 設定、CLI 進入點）
├── conftest.py             讓 pytest 找得到 drinkshop 套件
├── run_tests.py            不需要 pytest 的測試執行器
├── hello.py                最小可執行範例
├── drinkshop/
│   ├── __init__.py         套件的「大門」：決定公開介面
│   ├── errors.py           自訂例外
│   ├── menu.py             📦 資料：菜單（改價格只改這裡）
│   ├── pricing.py          🧮 純函式：計價邏輯
│   ├── orders.py           🧮 純函式：訂單模型與結帳
│   ├── report.py           🧮 純函式：報表與統計
│   ├── storage.py          💾 唯一碰硬碟的模組
│   └── cli.py              🖥 唯一做互動的模組
└── tests/
    ├── test_pricing.py     19 個測試
    ├── test_orders.py      21 個測試
    ├── test_storage.py     12 個測試
    └── test_report.py      23 個測試
                            ─────────
                            75 個測試 + 16 個 doctest
```

### 為什麼這樣拆？

| 原則 | 在這個專案裡的體現 |
| --- | --- |
| **按職責拆，不按型別拆** | `pricing` / `orders` / `report`，不是 `functions.py` / `classes.py` |
| **資料和邏輯分開** | `menu.py` 只有資料，阿宏調價不會碰到任何計算程式 |
| **把副作用推到邊界** | 只有 `storage.py` 碰硬碟、只有 `cli.py` 做互動 |
| **測試對應原始檔** | `pricing.py` ↔ `test_pricing.py`，一眼知道去哪找 |

**結果**：90% 的程式是純函式，用三行 `assert` 就能測，整套測試 0.05 秒跑完。

---

## 測試套件的看點

執行 `pytest -v` 或 `python3 run_tests.py`，注意這幾件事：

**1. 測試名稱就是規格書**

```
test_逢五進一而不是銀行家捨入
test_會員未滿門檻不打折
test_剛好達到門檻就打折
test_員工價蓋過一切折扣
test_空訂單的平均是零而不是除以零錯誤
```

把這些名字列出來，你不用讀任何程式就知道這個系統的規則。

**2. 每個 `raise` 都有對應的測試**

錯誤處理也是功能。`test_品項不存在要拋出MenuItemNotFound`、
`test_不合法的輸入一律拋出InvalidInput`、`test_庫存不足要拋出OutOfStock`。

**3. 邊界值被釘死**

`MEMBER_THRESHOLD - 1` / `MEMBER_THRESHOLD` / `500`、空清單、數量為 0、剛好扣完庫存。

**4. 跨平台的回歸測試**

| 測試 | 防止什麼 |
| --- | --- |
| `test_中文以utf8儲存` | Windows 預設 cp950 造成的亂碼 |
| `test_給Excel的CSV帶有BOM` | Excel 開中文 CSV 變亂碼 |
| `test_JSON裡的中文不是轉義序列` | 忘記 `ensure_ascii=False` |
| `test_測試結束後不留垃圾檔` | 寫死 `/tmp` 路徑 |
| `test_日報表的星期名稱不受系統語系影響` | `strftime("%A")` 在不同機器輸出不同 |

**5. 測試不依賴「今天是幾號」**

`report.py` 的 `daily_report(orders, on=...)` 把日期當參數。
`cli.py` 的 `make_demo_orders(..., seed=...)` 把亂數種子當參數。
**不可控的東西一律變成參數** —— 這是 TDD 最重要的設計副產品。

---

## 兩種測試執行方式的對照

| | `python3 run_tests.py` | `pytest` |
| --- | --- | --- |
| 需要安裝 | ❌ | ✅ |
| 測試報表 | 基本 | 漂亮、有顏色 |
| assert 失敗訊息 | 只有你寫的訊息 | 自動拆解運算式 |
| 只跑部分 | `run_tests.py 會員` | `pytest -k 會員` |
| 只重跑失敗的 | ❌ | `pytest --lf` |
| doctest | `--doctest` | `--doctest-modules`（已設定） |

`run_tests.py` 只有 40 行核心邏輯，**它就是 pytest 骨架的最小版本**：
找出 `test_` 開頭的函式、呼叫它、統計結果。打開來看一眼，你會發現測試框架沒有魔法。

---

## 安裝成正式套件（選配）

```bash
python3 -m pip install -e .          # -e = editable，改程式碼立刻生效
drinkshop demo                       # 裝完之後可以直接這樣用
python3 -m pip install -e ".[dev]"   # 連 pytest 一起裝
```

裝完之後在**任何目錄**都能 `import drinkshop`，不用再煩惱 `ModuleNotFoundError`。
