# %% [markdown]
# # 第 9 章：檔案與路徑（跨平台重點章）
#
# > 🎬 **情境**
# > 阿宏：「今天的營收多少？」
# > 你：「等我把今天的訂單重新輸入一次……」
# >
# > 程式一關掉資料就全沒了。而且阿宏要「這個月每天的趨勢」—— 那是 30 天的資料。
# >
# > 更麻煩的是：你用 Mac、小美用 Windows、阿宏的 POS 機是 Linux。
# > **同一份程式要在三台機器上都能跑。**
#
# 這是全書**跨平台差異最集中**的一章。

# %% [markdown]
# ## 9.1 😩 土法煉鋼：寫死路徑
#
# 網路上你會看到這種程式碼：
#
# ```python
# f = open("C:\\Users\\Amy\\Desktop\\訂單.csv")     # 🪟 只有小美能跑
# f = open("/Users/rex/Desktop/訂單.csv")          # 🍎 只有你能跑
# f = open("/home/ahong/orders.csv")               # 🐧 只有阿宏能跑
# ```
#
# 1. **換一台電腦就壞**（換使用者名稱也壞）
# 2. **換作業系統就壞**（`\` vs `/`）
# 3. **無法測試**（測試機器上沒有那個檔案）

# %%
# 還有一個隱形殺手
路徑字串 = "C:\temp\new.csv"
print("你以為是：C:\\temp\\new.csv")
print("實際上是：", repr(路徑字串), "← \\t 變成 Tab、\\n 變成換行！")

# %% [markdown]
# ## 9.2 💡 pathlib：從此不用煩惱斜線
#
# **忘掉 `os.path` 和字串拼接。Python 3.4 之後，路徑就用 `pathlib.Path`。**

# %%
from pathlib import Path
import platform

資料夾 = Path("工作區")
檔案 = 資料夾 / "2026-09-20.csv"        # 用 / 組路徑！

print("你的系統：", platform.system())
print("路徑長這樣：", 檔案)
print("\n同一行程式，在不同系統會自動變成：")
print("  🍎🐧  工作區/2026-09-20.csv")
print("  🪟    工作區\\2026-09-20.csv")

# %%
p = Path("工作區") / "2026-09-20.csv"

print("name  :", p.name)      # 檔名
print("stem  :", p.stem)      # 不含副檔名
print("suffix:", p.suffix)    # 副檔名
print("parent:", p.parent)    # 上層資料夾
print("parts :", p.parts)
print("exists:", p.exists())

# %%
# 幾個重要的「起點」
print("目前工作目錄 Path.cwd() :", Path.cwd())
print("使用者家目錄 Path.home():", Path.home())
print("\nNotebook 裡沒有 __file__，但在 .py 檔裡你會這樣寫：")
print('  專案根目錄 = Path(__file__).resolve().parent.parent')

# %% [markdown]
# > 🔍 **`Path.cwd()` 和 `Path(__file__)` 的差別很重要：**
# >
# > - `Path.cwd()` = 「你在哪裡執行 python」→ **會變**
# > - `Path(__file__)` = 「這個程式檔放在哪」→ **固定**
# >
# > 要找專案裡的資料檔，**一律用 `__file__` 推算**。
# > 用 `cwd()` 的程式，從別的目錄執行就會找不到檔案。

# %%
# 建立工作區（本章所有檔案都放這裡，最後會清乾淨）
工作區 = Path("工作區")
工作區.mkdir(exist_ok=True)               # 已存在也不報錯
(工作區 / "資料" / "2026-09").mkdir(parents=True, exist_ok=True)   # 連中間層一起建

print("🟢 建好了：")
for 路徑 in sorted(工作區.rglob("*")):
    print("  ", 路徑)

# %% [markdown]
# ## 9.3 ⚠️⚠️ 編碼：中文使用者的頭號地雷

# %%
import locale
import sys

print("你的系統預設編碼：", locale.getpreferredencoding(False))
print("Python 的檔案系統編碼：", sys.getfilesystemencoding())

# %% [markdown]
# `open()` 不指定 `encoding` 時，會用「系統預設編碼」：
#
# | 系統 | 預設編碼 |
# | --- | --- |
# | 🍎 macOS / 🐧 Linux | UTF-8 |
# | 🪟 Windows（繁中） | **cp950（Big5）** |
#
# 你在 Mac 上寫的 UTF-8 檔案，小美在 Windows 上用預設編碼讀，會得到：
#
# ```
# UnicodeDecodeError: 'cp950' codec can't decode byte 0xe7 in position 0
# ```
#
# 或更可怕的 —— **不報錯，但內容變成亂碼**（`ç­è¨` 這種）。

# %%
# 親眼看看編碼錯誤長什麼樣
測試檔 = 工作區 / "編碼測試.txt"
測試檔.write_text("珍珠奶茶 65 元", encoding="utf-8")

print("用 UTF-8 讀 →", 測試檔.read_text(encoding="utf-8"))

try:
    print("用 Big5 讀 →", 測試檔.read_text(encoding="big5"))
except UnicodeDecodeError as 錯誤:
    print("🔴 UnicodeDecodeError：", 錯誤)
    print("   這就是小美在 Windows 上會看到的畫面。")

# %%
# 更可怕的情況：不報錯，但是亂碼
原始位元組 = "珍珠奶茶".encode("utf-8")
亂碼 = 原始位元組.decode("latin-1")        # 用錯的編碼解讀，卻不會報錯
print("亂碼版本：", 亂碼)
print("→ 程式繼續跑，資料已經壞了，你三天後才發現。")

# %% [markdown]
# ### ✅ 鐵則：每一次讀寫文字檔，都明確寫 `encoding="utf-8"`
#
# ```python
# open(路徑, "r", encoding="utf-8")
# 路徑.read_text(encoding="utf-8")
# 路徑.write_text(內容, encoding="utf-8")
# ```
#
# **沒有例外。** 這一個習慣可以省掉你未來 90% 的中文亂碼問題。
#
# > 🔍 Python 3.15 起預設編碼將改為 UTF-8（PEP 686），
# > 但在那之前、以及面對舊系統時，明確指定仍是唯一安全的做法。

# %% [markdown]
# ## 9.4 open() 與 with

# %%
路徑 = 工作區 / "訂單.txt"

# ✖ 不好：忘記關檔；中間若出錯，close() 永遠不會執行
f = open(路徑, "w", encoding="utf-8")
f.write("珍珠奶茶 65\n")
f.close()

# ✔ 正確：with 會自動關檔，即使中間爆炸也一樣
with open(路徑, "a", encoding="utf-8") as f:
    f.write("冬瓜檸檬 45\n")

print(路徑.read_text(encoding="utf-8"))

# %% [markdown]
# **永遠用 `with`。** 這個語法叫 *context manager*，用途是「確保收尾一定會做」。

# %%
# with 的保證：即使中間爆炸，檔案還是會被關掉
try:
    with open(路徑, "a", encoding="utf-8") as f:
        f.write("紅茶 35\n")
        raise ValueError("中途出事了！")
except ValueError as 錯誤:
    print("🔴 發生錯誤：", 錯誤)

print("檔案關了嗎？", f.closed, "← with 保證會關")

# %% [markdown]
# ### 模式
#
# | 模式 | 意思 | 檔案不存在 | 檔案已存在 |
# | --- | --- | --- | --- |
# | `"r"` | 讀取（預設） | ❌ 報錯 | 讀 |
# | `"w"` | 寫入 | 建立 | ⚠️ **清空** |
# | `"a"` | 附加 | 建立 | 加在後面 |
# | `"x"` | 獨佔建立 | 建立 | ❌ 報錯（防止覆蓋） |
# | `"rb"` / `"wb"` | 二進位 | | 圖片影片用，**不要加 encoding** |

# %%
# ⚠️ "w" 會直接清空整個檔案
print("寫入前：", repr(路徑.read_text(encoding="utf-8")))
with open(路徑, "w", encoding="utf-8") as f:
    f.write("只剩這行\n")
print("用 w 之後：", repr(路徑.read_text(encoding="utf-8")), "← 之前的全沒了")

# 怕覆蓋就用 "x"
try:
    with open(路徑, "x", encoding="utf-8") as f:
        f.write("不會執行到")
except FileExistsError as 錯誤:
    print("🟢 用 x 模式擋下覆蓋：", type(錯誤).__name__)

# %%
# 三種讀法
路徑.write_text("珍珠奶茶 65\n冬瓜檸檬 45\n紅茶 35\n", encoding="utf-8")

with open(路徑, encoding="utf-8") as f:
    print("read()      →", repr(f.read()))

with open(路徑, encoding="utf-8") as f:
    print("readlines() →", f.readlines())

with open(路徑, encoding="utf-8") as f:
    print("逐行（大檔案一定用這個）：")
    for 行號, 行 in enumerate(f, 1):
        print(f"   {行號}. {行.rstrip()}")

# %% [markdown]
# > 🔍 **為什麼大檔案要逐行讀？**
# > `f.read()` 會把整個檔案載入記憶體。1 GB 的日誌檔會直接吃掉 1 GB RAM。
# > 逐行讀是「用多少讀多少」。**養成逐行讀的習慣，你永遠不會遇到記憶體爆掉。**

# %% [markdown]
# ## 9.5 CSV：試算表的通用格式

# %%
import csv

csv路徑 = 工作區 / "訂單.csv"

with csv路徑.open("w", encoding="utf-8", newline="") as f:      # ⚠️ newline=""
    writer = csv.writer(f)
    writer.writerow(["品項", "杯型", "金額"])
    writer.writerow(["珍珠奶茶", "大杯", 65])
    writer.writerow(["冬瓜檸檬", "中杯", 40])

print(csv路徑.read_text(encoding="utf-8"))

# %% [markdown]
# ⚠️ **寫 CSV 一定要加 `newline=""`。**
# 不加的話，Windows 上每一列之間會多一個空行（因為 `\r\n` 被轉換兩次）。
# 這是 csv 模組文件明確要求的寫法，請無腦照做。

# %%
with csv路徑.open(encoding="utf-8", newline="") as f:
    for 列 in csv.reader(f):
        print(列)

print("\n⚠️ 注意金額是 '65' 字串，不是 65 整數 —— CSV 讀進來全部是字串。")

# %%
# DictReader / DictWriter（推薦）
with csv路徑.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["品項", "杯型", "金額"])
    writer.writeheader()
    writer.writerow({"品項": "珍珠奶茶", "杯型": "大杯", "金額": 65})
    writer.writerow({"品項": "冬瓜檸檬", "杯型": "中杯", "金額": 40})

總額 = 0
with csv路徑.open(encoding="utf-8", newline="") as f:
    for 列 in csv.DictReader(f):
        金額 = int(列["金額"])              # 用名字取，而且記得轉型
        print(f"{列['品項']:<10}{金額:>5}")
        總額 += 金額
print(f"{'總計':<10}{總額:>5}")

# %% [markdown]
# **為什麼推薦 `DictReader`？**
# 別人在 CSV 中間插入一個欄位時，用 `列[2]` 的程式會默默算錯，
# 用 `列["金額"]` 的程式完全不受影響。
#
# ⚠️ **給 Excel 看的 CSV 要用 `encoding="utf-8-sig"`**，
# 否則中文在 Excel 裡會變亂碼（BOM 會告訴 Excel「這是 UTF-8」）。

# %%
excel版 = 工作區 / "給阿宏看的報表.csv"
with excel版.open("w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f).writerow(["品項", "金額"])

print("utf-8-sig 檔案的前 3 個 byte：", excel版.read_bytes()[:3], "← 這就是 BOM")

# %% [markdown]
# ## 9.6 JSON：程式之間交換資料的標準
#
# CSV 只能存「表格」，JSON 可以存巢狀結構（像阿宏的菜單）。

# %%
import json

菜單 = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
}

json路徑 = 工作區 / "菜單.json"
with json路徑.open("w", encoding="utf-8") as f:
    json.dump(菜單, f, ensure_ascii=False, indent=2)

print(json路徑.read_text(encoding="utf-8"))

# %%
# ⚠️ 不加 ensure_ascii=False 的下場
print(json.dumps(菜單, indent=2)[:80], "...")
print("\n↑ 中文被存成 \\uXXXX，還是讀得回來，但人看不懂而且檔案變大。")

# %%
with json路徑.open(encoding="utf-8") as f:
    讀回 = json.load(f)

assert 讀回 == 菜單                   # 完整保留結構和型別
print("🟢 讀回來和原本一模一樣：", 讀回["珍珠奶茶"]["大杯"], type(讀回["珍珠奶茶"]["大杯"]).__name__)

# %% [markdown]
# | 函式 | 做什麼 |
# | --- | --- |
# | `json.dump(物件, 檔案)` | 寫進**檔案** |
# | `json.dumps(物件)` | 轉成**字串**（多一個 s = string） |
# | `json.load(檔案)` | 從**檔案**讀 |
# | `json.loads(字串)` | 從**字串**讀 |
#
# ### CSV vs JSON 怎麼選
#
# | | CSV | JSON |
# | --- | --- | --- |
# | 結構 | 只能平面表格 | 可巢狀 |
# | Excel 能開 | ✔ | ✖ |
# | 型別 | 全部是字串 | 保留數字/布林/null |
# | 適合 | 交易紀錄、報表 | 設定檔、菜單、API |

# %% [markdown]
# ## 9.7 🧪 測試會碰檔案的程式
#
# **這是本章最重要的一節。** 檔案 I/O 是最難測的東西，因為它有副作用。

# %% [markdown]
# ### ❌ 錯誤做法
#
# ```python
# def test_存檔():
#     存檔("/tmp/test.csv", 資料)           # 🪟 Windows 沒有 /tmp
#     assert Path("/tmp/test.csv").exists()
#     # 而且測試結束後垃圾檔留在硬碟上
# ```

# %%
# ✅ 正確做法：標準庫的 tempfile（不用 pytest 也能跨平台）
import tempfile


def 存訂單(訂單, 路徑: Path) -> None:
    with Path(路徑).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["品項", "金額"])
        writer.writeheader()
        writer.writerows(訂單)


def 讀訂單(路徑: Path) -> list[dict]:
    with Path(路徑).open(encoding="utf-8", newline="") as f:
        return [{"品項": 列["品項"], "金額": int(列["金額"])} for 列 in csv.DictReader(f)]


def test_存檔再讀回應該一模一樣():
    訂單 = [{"品項": "珍珠奶茶", "金額": 65}, {"品項": "紅茶", "金額": 35}]

    with tempfile.TemporaryDirectory() as 暫存:
        檔案 = Path(暫存) / "訂單.csv"
        存訂單(訂單, 檔案)
        assert 讀訂單(檔案) == 訂單
    # 離開 with 就自動刪除整個目錄，跨平台、不留垃圾


test_存檔再讀回應該一模一樣()
print("🟢 round-trip 測試通過（存進去再讀出來，要一模一樣）")

# %% [markdown]
# ✅ **pytest 使用者的版本**（更簡潔）：
#
# ```python
# def test_存檔(tmp_path):              # pytest 自動注入
#     檔案 = tmp_path / "訂單.csv"       # 每個測試一個全新的暫存目錄
#     存訂單(訂單, 檔案)
#     assert 讀訂單(檔案) == 訂單
#     # 測試結束後 pytest 自動清理
# ```

# %% [markdown]
# ### ✅ 最佳做法：讓大部分程式「根本不碰檔案」

# %%
# ✖ 難測：計算和存檔混在一起
def 產生日報表並存檔(訂單, 路徑):
    總額 = sum(o["金額"] for o in 訂單)
    Path(路徑).write_text(f"總額:{總額}", encoding="utf-8")


# ✔ 好測：拆成純函式 + 薄薄一層 I/O
def 產生日報表(訂單) -> str:                    # 純函式，三行測試搞定
    總額 = sum(o["金額"] for o in 訂單)
    return f"總額:{總額}"


def 存檔(內容: str, 路徑: Path) -> None:        # 只有這個需要碰硬碟
    Path(路徑).write_text(內容, encoding="utf-8")


# 95% 的邏輯現在可以用純粹的 assert 測
assert 產生日報表([{"金額": 65}, {"金額": 45}]) == "總額:110"
assert 產生日報表([]) == "總額:0"                # 邊界：空訂單
print("🟢 兩行測試，不碰硬碟，毫秒完成")

# %% [markdown]
# > 🔍 **這就是第 8 章說的「把副作用推到邊界」。**
# >
# > 你會發現：**為了讓程式好測試而做的設計，剛好就是好的設計。**
# > 這是 TDD 最大的附加價值 —— 它不只在抓 bug，它在改善你的架構。

# %% [markdown]
# ## 9.8 實戰：把一整個月的資料讀進來

# %%
# 先造 5 天的假資料
import random

random.seed(20260920)                        # 固定亂數種子，結果可重現 ← 測試友善
日資料目錄 = 工作區 / "資料" / "2026-09"

for 日 in range(16, 21):
    檔案 = 日資料目錄 / f"2026-09-{日}.csv"
    with 檔案.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["品項", "金額"])
        w.writeheader()
        for _ in range(random.randint(3, 6)):
            w.writerow({"品項": random.choice(["珍珠奶茶", "冬瓜檸檬", "紅茶"]),
                        "金額": random.choice([35, 45, 55, 65])})

print("建立的檔案：")
for p in sorted(日資料目錄.glob("*.csv")):
    print("  ", p.name)

# %%
# 用 glob 一次讀完整個月
月營收 = {}
for 檔案 in sorted(日資料目錄.glob("*.csv")):
    with 檔案.open(encoding="utf-8", newline="") as f:
        月營收[檔案.stem] = sum(int(列["金額"]) for 列 in csv.DictReader(f))

print(f"{'日期':<14}{'營收':>8}")
print("-" * 22)
for 日期, 營收 in 月營收.items():
    print(f"{日期:<14}{營收:>8,}")
print("-" * 22)
print(f"{'合計':<14}{sum(月營收.values()):>8,}")

# %% [markdown]
# `glob("*.csv")` 一行就抓到所有符合的檔案。
# 要遞迴找子資料夾用 `rglob("*.csv")`。

# %%
print("rglob 遞迴找整個工作區的 csv：")
for p in sorted(工作區.rglob("*.csv")):
    print("  ", p)

# %% [markdown]
# ## 9.9 ⚠️ 跨平台檢查清單
#
# | 檢查項 | ❌ 不要 | ✅ 要 |
# | --- | --- | --- |
# | 組路徑 | `"資料/" + 檔名` | `Path("資料") / 檔名` |
# | 絕對路徑 | `"C:\\Users\\..."` | `Path(__file__).parent`、`Path.home()` |
# | 編碼 | `open(p)` | `open(p, encoding="utf-8")` |
# | 寫 CSV | `open(p, "w")` | `open(p, "w", newline="", encoding="utf-8")` |
# | 暫存檔 | `/tmp/x.csv` | `tempfile` 或 pytest `tmp_path` |
# | 換行 | 寫死 `"\r\n"` | 交給 Python 處理 |
# | 大小寫 | 假設不分大小寫 | 🪟 不分、🍎🐧 **分**，一律當成有分 |
# | 執行指令 | `os.system("ls")` | `subprocess.run([...])`，或根本別呼叫系統指令 |
#
# > ⚠️ **檔名大小寫特別容易中招**：
# > 你在 Mac 上寫 `open("Data.csv")` 而實際檔名是 `data.csv` —— Mac 預設不分大小寫，**能跑**。
# > 部署到 Linux 伺服器，立刻 `FileNotFoundError`。這是超常見的上線事故。

# %%
# 示範：不存在的檔案
try:
    (工作區 / "不存在的檔案.csv").read_text(encoding="utf-8")
except FileNotFoundError as 錯誤:
    print("🔴 FileNotFoundError：", 錯誤)
    print("   第 11 章會教你怎麼優雅地處理這種情況。")

# %% [markdown]
# ## 9.10 清理

# %%
import shutil

shutil.rmtree(工作區)
print("🟢 清理完成，硬碟上不留東西")
print("工作區還在嗎？", 工作區.exists())

# %% [markdown]
# ## 📌 本章速記
#
# ```python
# from pathlib import Path
#
# p = Path("資料") / "2026-09-20.csv"          # 永遠這樣組路徑
# p.name  p.stem  p.suffix  p.parent  p.exists()
# Path("資料").mkdir(parents=True, exist_ok=True)
# list(Path("資料").glob("*.csv"))             # rglob 遞迴
# p.unlink(missing_ok=True)
#
# Path.cwd()                                  # 執行位置（會變）
# Path(__file__).resolve().parent             # 程式檔位置（固定）← 找專案資料用這個
#
# p.write_text("內容", encoding="utf-8")       # 每次都寫 encoding！
# with open(p, encoding="utf-8") as f:
#     for 行 in f: ...                         # 大檔案逐行讀
#
# # 模式：r 讀 / w ⚠️清空 / a 附加 / x 防覆蓋 / rb wb 二進位
#
# csv：open(p, "w", encoding="utf-8", newline="")   # newline="" 不可少
#      給 Excel 用 encoding="utf-8-sig"
# json：json.dump(物件, f, ensure_ascii=False, indent=2)
#
# 測試：tempfile.TemporaryDirectory() 或 pytest 的 tmp_path
#      最好的做法：讓邏輯根本不碰檔案
# ```

# %% [markdown]
# ---
# ## 🧪 練習
#
# **練習 9-1：round-trip 測試**
# 寫 `存訂單(訂單, 路徑)` 和 `讀訂單(路徑)`，要求：CSV 有標題列、讀回來金額是 `int`、
# 用 `tempfile` 測試不留垃圾檔。（9.7 節有完整答案可以對照）
#
# **練習 9-2：找出跨平台問題**
# ```python
# def 存日報表(資料):
#     with open("C:\\reports\\" + str(date.today()) + ".csv", "w") as f:
#         f.write(資料)
# ```
# 這幾行有**幾個**跨平台問題？列出來並改寫。（提示：至少 4 個）
#
# **練習 9-3：把難測的函式拆開**
# ```python
# def 統計並存檔(訂單, 路徑):
#     總額 = sum(o["金額"] for o in 訂單)
#     平均 = 總額 / len(訂單)
#     with open(路徑, "w", encoding="utf-8") as f:
#         f.write(f"總額 {總額} 平均 {平均:.1f}")
# ```
# 拆成「純函式 + 存檔」兩個，並為純函式寫三個測試（含空清單邊界 —— 注意它現在會 `ZeroDivisionError`）。

# %% [markdown]
# ---
# ➡️ 下一章：`10-類別與物件.ipynb` —— 一筆訂單有 8 個欄位，參數傳到你懷疑人生。
