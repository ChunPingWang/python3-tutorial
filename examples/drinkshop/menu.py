"""菜單資料。

這個模組「只有資料，沒有邏輯」——
阿宏要調整價格時只需要改這裡，不會碰到任何計算程式。
"""

from __future__ import annotations

SIZES: tuple[str, ...] = ("中杯", "大杯")

MENU: dict[str, dict[str, int]] = {
    "珍珠奶茶": {"中杯": 55, "大杯": 65},
    "冬瓜檸檬": {"中杯": 40, "大杯": 45},
    "紅茶拿鐵": {"中杯": 50, "大杯": 60},
    "四季春茶": {"中杯": 30, "大杯": 35},
    "百香果綠": {"中杯": 45, "大杯": 55},
    "黑糖鮮奶": {"中杯": 60, "大杯": 70},
}


def item_names() -> list[str]:
    """回傳所有品項名稱。

    >>> "珍珠奶茶" in item_names()
    True
    """
    return list(MENU)


def has_item(name: str, size: str | None = None) -> bool:
    """菜單上有這個品項（以及杯型）嗎？

    >>> has_item("珍珠奶茶")
    True
    >>> has_item("綠茶")
    False
    >>> has_item("珍珠奶茶", "特大杯")
    False
    """
    if name not in MENU:
        return False
    return size is None or size in MENU[name]
