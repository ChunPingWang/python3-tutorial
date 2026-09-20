"""storage 模組的測試 —— 唯一會碰硬碟的測試。

三個跨平台要點:

1. **絕對不寫死路徑**(`/tmp/x.csv` 在 Windows 上不存在)
2. 用 `tempfile.TemporaryDirectory()`,離開 with 自動刪除
3. 全部用 `pathlib.Path` 組路徑

pytest 使用者可以改用更簡潔的 `tmp_path` fixture:

    def test_存檔(tmp_path):
        path = tmp_path / "訂單.csv"
        ...
"""

import tempfile
from datetime import date
from pathlib import Path

from drinkshop.orders import Order
from drinkshop.storage import (
    export_for_excel,
    load_menu,
    load_month,
    load_orders,
    save_menu,
    save_orders,
)

SAMPLE = [
    Order("珍珠奶茶", "大杯", 2, is_member=True, ordered_on=date(2026, 9, 20)),
    Order("四季春茶", "中杯", 1, ordered_on=date(2026, 9, 20)),
]


def test_存檔再讀回來要一模一樣():
    """round-trip 測試:存進去再讀出來,資料不能變。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "訂單.csv"
        save_orders(SAMPLE, path)
        loaded = load_orders(path)

    assert loaded == SAMPLE          # 靠 dataclass 的 __eq__，一行就比完


def test_讀回來的數量是整數不是字串():
    """CSV 讀進來全部是字串，忘了轉型是最常見的 bug。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "訂單.csv"
        save_orders(SAMPLE, path)
        loaded = load_orders(path)

    assert isinstance(loaded[0].quantity, int)
    assert isinstance(loaded[0].ordered_on, date)


def test_上層資料夾不存在會自動建立():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "還沒存在的" / "資料夾" / "訂單.csv"
        save_orders(SAMPLE, path)
        assert path.exists()


def test_存檔內容是可讀的CSV():
    with tempfile.TemporaryDirectory() as tmp:
        path = save_orders(SAMPLE, Path(tmp) / "訂單.csv")
        text = path.read_text(encoding="utf-8")

    assert text.startswith("日期,品項,杯型,數量,會員,金額")
    assert "珍珠奶茶" in text


def test_空訂單也能存檔():
    with tempfile.TemporaryDirectory() as tmp:
        path = save_orders([], Path(tmp) / "空的.csv")
        assert load_orders(path) == []


def test_中文以utf8儲存():
    """明確指定 encoding 的回歸測試。

    Windows 的預設編碼是 cp950，不指定的話中文會壞掉。
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = save_orders(SAMPLE, Path(tmp) / "訂單.csv")
        raw = path.read_bytes()

    assert "珍珠奶茶".encode("utf-8") in raw


def test_菜單存成JSON再讀回來():
    menu = {"珍珠奶茶": {"中杯": 55, "大杯": 65}}
    with tempfile.TemporaryDirectory() as tmp:
        path = save_menu(menu, Path(tmp) / "菜單.json")
        assert load_menu(path) == menu


def test_JSON裡的中文不是轉義序列():
    """ensure_ascii=False 的回歸測試。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = save_menu({"珍珠奶茶": {"大杯": 65}}, Path(tmp) / "菜單.json")
        text = path.read_text(encoding="utf-8")

    assert "珍珠奶茶" in text
    assert "\\u" not in text


def test_讀取整個月的資料夾():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / "2026-09"
        for day in ("2026-09-19", "2026-09-20"):
            save_orders(SAMPLE, folder / f"{day}.csv")

        by_day = load_month(folder)

    assert sorted(by_day) == ["2026-09-19", "2026-09-20"]
    assert by_day["2026-09-20"] == SAMPLE


def test_資料夾是空的就回傳空字典():
    with tempfile.TemporaryDirectory() as tmp:
        assert load_month(Path(tmp)) == {}


def test_給Excel的CSV帶有BOM():
    """utf-8-sig 的回歸測試 —— 沒有 BOM 的話 Excel 開中文會是亂碼。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = export_for_excel([{"品項": "珍珠奶茶", "金額": 65}], Path(tmp) / "報表.csv")
        head = path.read_bytes()[:3]

    assert head == b"\xef\xbb\xbf"


def test_測試結束後不留垃圾檔():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "訂單.csv"
        save_orders(SAMPLE, path)
        assert path.exists()
    assert not path.exists(), "離開 with 之後暫存目錄應該被刪掉"
