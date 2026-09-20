"""阿宏手搖飲營運工具。

這個 __init__.py 是套件的「大門」:它決定使用者看得到什麼。
有了它,別人可以寫

    from drinkshop import Order, line_price

而不需要知道這些東西實際住在哪個檔案 —— 你之後重構內部結構時,
只要這裡的介面不變,使用者的程式就完全不用改。這叫「封裝」。
"""

from drinkshop.errors import (
    DrinkShopError,
    InvalidInput,
    MenuItemNotFound,
    OutOfStock,
)
from drinkshop.menu import MENU, SIZES, has_item, item_names
from drinkshop.orders import Order, checkout, deduct_stock, parse_quantity
from drinkshop.pricing import line_price, round_half_up, unit_price, with_tax
from drinkshop.report import daily_report, revenue, slow_movers, top_items

__version__ = "1.0.0"

__all__ = [
    # 資料
    "MENU",
    "SIZES",
    "item_names",
    "has_item",
    # 計價
    "round_half_up",
    "unit_price",
    "line_price",
    "with_tax",
    # 訂單
    "Order",
    "parse_quantity",
    "checkout",
    "deduct_stock",
    # 報表
    "revenue",
    "top_items",
    "slow_movers",
    "daily_report",
    # 例外
    "DrinkShopError",
    "MenuItemNotFound",
    "OutOfStock",
    "InvalidInput",
    "__version__",
]
