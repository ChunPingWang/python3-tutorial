"""讀寫檔案 —— 這個套件裡**唯一**碰硬碟的模組。

把所有副作用集中在這裡,其他模組就都是純函式,三行測試就能驗證。
這個設計原則叫「把副作用推到邊界」。

跨平台注意事項(三個都在這個檔案裡實踐):

1. 路徑一律用 pathlib.Path,不做字串拼接
2. 每次讀寫文字檔都明確指定 encoding
3. 寫 CSV 一定要 newline=""(否則 Windows 上每列之間會多一個空行)
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from drinkshop.orders import Order

#: CSV 欄位順序
FIELDNAMES = ["日期", "品項", "杯型", "數量", "會員", "金額"]


def save_orders(orders: list[Order], path: str | Path) -> Path:
    """把訂單寫成 CSV,回傳實際寫入的路徑。

    上層資料夾不存在時會自動建立。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for order in orders:
            writer.writerow(
                {
                    "日期": (order.ordered_on or date.today()).isoformat(),
                    "品項": order.item,
                    "杯型": order.size,
                    "數量": order.quantity,
                    "會員": "Y" if order.is_member else "N",
                    "金額": order.total,
                }
            )
    return path


def load_orders(path: str | Path) -> list[Order]:
    """從 CSV 讀回訂單。

    注意 CSV 讀進來全部是字串,數字欄位一定要自己轉型。
    """
    path = Path(path)
    orders: list[Order] = []

    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            orders.append(
                Order(
                    item=row["品項"],
                    size=row["杯型"],
                    quantity=int(row["數量"]),          # ← 記得轉型
                    is_member=row["會員"] == "Y",
                    ordered_on=date.fromisoformat(row["日期"]),
                )
            )
    return orders


def save_menu(menu: dict, path: str | Path) -> Path:
    """把菜單存成 JSON。

    ensure_ascii=False 讓中文以原樣存檔(不然會變成 \\uXXXX),
    sort_keys=True 讓 git diff 乾淨。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def load_menu(path: str | Path) -> dict:
    """從 JSON 讀回菜單。"""
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def load_month(folder: str | Path) -> dict[str, list[Order]]:
    """讀取一整個資料夾的日報 CSV,回傳 {日期字串: 訂單清單}。

    用 glob 一次抓完所有檔案,檔名(不含副檔名)當成日期。
    """
    folder = Path(folder)
    result: dict[str, list[Order]] = {}
    for csv_path in sorted(folder.glob("*.csv")):
        result[csv_path.stem] = load_orders(csv_path)
    return result


def export_for_excel(rows: list[dict], path: str | Path) -> Path:
    """輸出給 Excel 開的 CSV。

    ⚠️ 用 utf-8-sig(帶 BOM),否則中文在 Excel 裡會是亂碼。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return path

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path
