# Python 3 教材：用情境學語法，用測試學正確

> 一本給初學者的 Python 3 教材。三個特色：
>
> 1. **情境驅動** — 每個語法都從一個真實需求長出來，先問「不用它我會有多痛」，再給解法。
> 2. **測試驅動** — 先把「我期待它做到什麼」寫成測試，再寫程式讓測試變綠。你從第 1 章就開始這樣做。
> 3. **到處都能跑** — Windows / macOS / Linux / Jupyter Notebook 全部驗證過，程式碼不挑作業系統。

---

## 這本教材的故事線

從第 1 章到第 14 章，你只做一件事：

> **幫「阿宏手搖飲」寫一套營運小工具。**

第 1 章你只會記下「一杯珍奶 65 元」；
到第 14 章，你會有一套能讀取整個月銷售檔案、算出營收排行、找出滯銷品項、還附帶 40 幾個自動化測試的完整程式。

每一章新增的功能，都是因為**上一章的做法撐不住了**：

| 章 | 阿宏丟給你的新需求 | 撐不住的地方 | 這章學到的解法 |
| --- | --- | --- | --- |
| 01 | 記下一筆訂單 | — | 變數、型別、`assert` |
| 02 | 印出一張漂亮的收據 | 數字接不進文字 | f-string、數值運算 |
| 03 | 會員打 9 折、加大加 10 元 | 價格不是固定的 | `if / elif / else` |
| 04 | 結算一整天 200 筆訂單 | 總不能複製貼上 200 次 | `for` / `while` |
| 05 | 管理菜單、庫存、今日賣出品項 | 一堆變數命名到崩潰 | list / dict / tuple / set |
| 06 | 三個地方都在算同一套價格 | 改價格要改三處 | 函式、參數、回傳值 |
| 07 | 改完價格不知道有沒有改壞 | 每次都要手動重試一遍 | **TDD：紅 → 綠 → 重構** |
| 08 | 程式長到 400 行，翻不動 | 全塞在一個檔案 | 模組、套件、`import` |
| 09 | 每天的銷售要存檔、明天讀回來 | 關掉程式資料就沒了 | `pathlib`、CSV、編碼 |
| 10 | 一筆訂單有品項、甜度、冰塊、會員… | 參數傳到第 8 個 | 類別與物件 |
| 11 | 客人輸入「兩杯」而不是「2」 | 程式直接崩潰 | 例外處理、除錯 |
| 12 | 要日期、JSON、統計、電話清洗 | 自己刻太慢 | 標準函式庫 |
| 13 | 要畫圖表給老闆看 | 標準庫沒有 | venv、pip、Jupyter 實務 |
| 14 | 全部整合成月報 | — | 用 TDD 從零做完一個專案 |

---

## 為什麼要「先寫測試」？

初學者最常見的學習方式是：**寫一段程式 → 執行 → 看畫面 → 覺得好像對 → 繼續**。

問題是「覺得好像對」不是知識。你不知道邊界在哪，也不知道明天改壞了沒。

這本教材換一個順序：

```python
# 第一步:先寫下你的期待(此時 price_of 根本還不存在)
assert price_of("珍珠奶茶") == 65

# 第二步:執行 → 紅燈(NameError: name 'price_of' is not defined)
# 第三步:寫剛好夠讓它變綠的程式
# 第四步:綠燈之後才整理、重構
```

這叫 **TDD（Test-Driven Development，測試驅動開發）**，三個節奏：

> 🔴 **紅燈**：寫一個會失敗的測試，說清楚你要什麼
> 🟢 **綠燈**：寫最少的程式讓它通過
> 🔵 **重構**：在測試保護下把程式整理乾淨

對初學者而言，TDD 真正的價值不是「品質管理」，而是：

- **逼你先講清楚需求**。寫不出 `assert`，代表你其實還不知道自己要做什麼。
- **給你即時回饋**。綠燈就是綠燈，不用猜。
- **讓你敢改程式**。有測試罩著，重構不再是賭博。

本教材的測試工具是循序漸進的，**前 6 章只用內建的 `assert`，不必安裝任何東西**：

| 階段 | 工具 | 需要安裝嗎 | 出現章節 |
| --- | --- | --- | --- |
| 1 | `assert` | ❌ 內建 | 01 起，全書 |
| 2 | `doctest`（把範例寫進說明文件，順便當測試） | ❌ 內建 | 07 |
| 3 | `unittest`（標準庫的測試框架） | ❌ 內建 | 07 |
| 4 | `pytest`（業界最常用） | ✅ `pip install pytest` | 07 起，選配 |

> `examples/` 裡的測試同時支援 pytest 與「不裝任何東西」的執行方式，見 [examples/README.md](examples/README.md)。

---

## 目錄

| # | 章節 | 情境 | 你會學到 |
| --- | --- | --- | --- |
| 00 | [環境安裝與 Jupyter](docs/00-環境安裝與-Jupyter.md) | 開工前 | 三平台安裝、終端機、Jupyter、虛擬環境 |
| 01 | [第一支程式與變數](docs/01-第一支程式與變數.md) | 記下一筆訂單 | 變數、型別、`print`、`assert`、註解 |
| 02 | [數字與字串](docs/02-數字與字串.md) | 印一張收據 | 四則運算、整除、`round`、f-string、字串方法 |
| 03 | [判斷：讓程式做選擇](docs/03-判斷.md) | 會員折扣 | `if/elif/else`、布林、比較、`and/or/not` |
| 04 | [迴圈：把重複的事交給電腦](docs/04-迴圈.md) | 結算一整天 | `for`、`range`、`while`、`break/continue` |
| 05 | [資料結構](docs/05-資料結構.md) | 菜單與庫存 | list、tuple、dict、set、推導式 |
| 06 | [函式](docs/06-函式.md) | 到處都在算價格 | 參數、回傳值、預設值、作用域、型別註記 |
| 07 | [測試驅動開發](docs/07-測試驅動開發.md) | 改壞了怎麼辦 | 紅綠重構、doctest、unittest、pytest |
| 08 | [模組與套件](docs/08-模組與套件.md) | 檔案太長 | `import`、`__name__`、套件目錄、匯入路徑 |
| 09 | [檔案與路徑（跨平台重點）](docs/09-檔案與路徑.md) | 資料要存下來 | `pathlib`、`open`、編碼、CSV、暫存目錄 |
| 10 | [類別與物件](docs/10-類別與物件.md) | 一筆訂單有太多欄位 | `class`、`__init__`、方法、`dataclass` |
| 11 | [例外與除錯](docs/11-例外與除錯.md) | 使用者亂輸入 | `try/except`、自訂例外、`logging`、`pdb` |
| 12 | [標準函式庫巡禮](docs/12-標準函式庫巡禮.md) | 別重造輪子 | `datetime`、`json`、`csv`、`re`、`collections`、`statistics` |
| 13 | [套件管理與 Jupyter 實務](docs/13-套件管理與-Jupyter-實務.md) | 要畫圖給老闆看 | venv、pip、requirements、magic 指令、繪圖中文字型 |
| 14 | [綜合專案：營運儀表板](docs/14-綜合專案.md) | 做出月報 | 用 TDD 從零完成一個可交付專案 |

**附錄**

- [附錄 A：語法速查表](docs/附錄A-速查表.md)
- [附錄 B：練習解答](docs/附錄B-練習解答.md)
- [附錄 C：疑難排解（含三平台差異）](docs/附錄C-疑難排解.md)

**可執行素材**

- [`notebooks/`](notebooks/) — 每章一本 Jupyter Notebook，全部實際執行驗證過
- [`examples/`](examples/) — 完整的 `drinkshop` 範例專案與測試套件

---

## 怎麼開始（三平台）

### 選項 A：只用 Jupyter Notebook（推薦初學者）

```bash
# 1. 確認 Python 版本(需要 3.10 以上,本教材以 3.12 撰寫)
python3 --version        # macOS / Linux
py -3 --version          # Windows

# 2. 建立虛擬環境並安裝 Jupyter
python3 -m venv .venv                    # macOS / Linux
source .venv/bin/activate
py -3 -m venv .venv                      # Windows
.venv\Scripts\activate

pip install -r requirements.txt

# 3. 開啟
jupyter lab            # 或 jupyter notebook
```

然後打開 `notebooks/00-環境檢查.ipynb`，從頭按 `Shift + Enter` 跑下去。

### 選項 B：只用終端機 + 編輯器

```bash
python3 examples/hello.py          # macOS / Linux
py -3 examples\hello.py            # Windows
```

章節裡的每段程式碼都可以直接貼進 `python3` 互動模式或存成 `.py` 檔執行。

### 選項 C：不想安裝任何東西

用瀏覽器打開 [Google Colab](https://colab.research.google.com/)，把 `notebooks/` 裡的 `.ipynb` 上傳即可。本教材刻意不使用任何本機專屬功能，Colab 上完全能跑。

---

## 排版約定

| 記號 | 意思 |
| --- | --- |
| `$ 指令` | 在終端機（Terminal / PowerShell）輸入，複製時不要複製 `$` |
| `>>> 程式` | 在 Python 互動模式輸入 |
| 🪟 / 🍎 / 🐧 | 只適用 Windows / macOS / Linux |
| 🔴 🟢 🔵 | TDD 的紅燈、綠燈、重構階段 |
| ⚠️ | 新手常踩的坑 |
| 🧪 | 動手練習（解答在附錄 B） |

每一章的結構都是固定的：

```
🎬 情境      → 阿宏提出的新需求
😩 土法煉鋼  → 用你目前會的東西硬做,以及它為什麼撐不住
🧪 先寫測試  → 把「我希望它做到什麼」寫成 assert(此時一定是紅燈)
💡 解法      → 這章的語法登場,讓測試變綠
🔍 深入一點  → 為什麼這樣設計、什麼時候該用、什麼時候不該用
⚠️ 常見錯誤  → 錯誤訊息長什麼樣、怎麼修
📌 本章速記  → 一頁帶走
🧪 練習      → 附測試,自己寫到全綠
```

---

## 這份教材自己也有測試

教材最糟的情況是「書上的程式貼上去跑不動」。所以：

| 素材 | 怎麼驗證 |
| --- | --- |
| 15 本 notebook | `tools/build_notebooks.py --check` 用 nbclient **實際執行每一格** |
| `examples/` 專案 | 75 個測試 + 29 個 doctest，`pytest` 與免安裝的 `run_tests.py` 都能跑 |
| 跨平台主張 | GitHub Actions 在 **Windows / macOS / Linux × Python 3.10 / 3.12** 上跑一遍 |

```bash
# 在本機驗證整份教材
python3 tools/build_notebooks.py --check     # 產生並執行所有 notebook
cd examples && python3 run_tests.py --doctest
```

### Notebook 的來源是 `.py`

`notebooks/*.ipynb` 是由 `notebooks/src/*.py`（percent 格式）產生的，
產生出來的 notebook **不含執行輸出**，所以 git diff 乾淨、衝突少。

```bash
python3 tools/build_notebooks.py             # 只產生
python3 tools/build_notebooks.py --check     # 產生並實際執行驗證
```

改教材請改 `notebooks/src/*.py`，不要直接改 `.ipynb`。

---

## 給教學者

- 每章的 notebook 都可以單獨發給學生，彼此不相依（需要前面章節的成果時會在第一格重新定義）。
- 練習題的測試都寫在 notebook 裡，學生按下執行就知道對不對，**不需要你逐份批改**。
- notebook 不含輸出，學生拿到的是乾淨的版本，必須自己執行才看得到結果。
- 每章結構固定（情境 → 土法煉鋼 → 先寫測試 → 解法 → 深入 → 常見錯誤 → 速記 → 練習），
  可以直接對應一堂課。
- 建議節奏：第 0~7 章各一堂（TDD 那章可拆兩堂），第 8~13 章各一堂，第 14 章當期末專案。

---

## 版本

- 撰寫依據：Python **3.12**（3.10 以上皆可；文中用到 3.10+ 語法處會標示）
- 最後驗證：2026-09，macOS 14 / Python 3.12.7
- 授權：教材內容與範例程式可自由用於教學
