"""計價邏輯。

這個模組裡全部都是**純函式**:同樣的輸入永遠得到同樣的輸出,
不讀檔案、不看時間、不改變任何外部狀態。

純函式的好處就是超好測試 —— 見 tests/test_pricing.py。
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from drinkshop.errors import MenuItemNotFound
from drinkshop.menu import MENU

#: 會員折扣（9 折）
MEMBER_RATE = 0.9
#: 會員折扣的消費門檻（含）
MEMBER_THRESHOLD = 200
#: 員工價（一律優先，不再套用任何折扣）
STAFF_PRICE = 40
#: 營業稅率
TAX_RATE = 0.05


def round_half_up(value: float) -> int:
    """台灣人習慣的四捨五入(逢五進一),回傳整數。

    Python 內建的 round() 用的是「銀行家捨入」,
    round(2.5) 會得到 2 而不是 3,阿宏會覺得你算錯。

    >>> round_half_up(58.5)
    59
    >>> round_half_up(2.5)
    3
    >>> round_half_up(204.75)
    205
    >>> round_half_up(0)
    0
    """
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def unit_price(name: str, size: str) -> int:
    """查出單價。

    品項或杯型不存在時拋出 MenuItemNotFound —— 這代表點餐系統有 bug,
    不應該默默算成 0 元。

    >>> unit_price("珍珠奶茶", "大杯")
    65
    """
    try:
        return MENU[name][size]
    except KeyError as exc:
        raise MenuItemNotFound(f"菜單上沒有「{name} / {size}」") from exc


def apply_member_discount(amount: int) -> int:
    """套用會員折扣;未達門檻則原價回傳。

    >>> apply_member_discount(199)
    199
    >>> apply_member_discount(200)
    180
    """
    if amount < MEMBER_THRESHOLD:
        return amount
    return round_half_up(amount * MEMBER_RATE)


def with_tax(amount: int) -> int:
    """加上營業稅(四捨五入到整數元)。

    >>> with_tax(195)
    205
    """
    return round_half_up(amount * (1 + TAX_RATE))


def line_price(
    name: str,
    size: str,
    quantity: int = 1,
    *,
    is_member: bool = False,
    is_staff: bool = False,
) -> int:
    """算出一筆明細的金額。

    規則優先序(阿宏親口確認過的):

    1. 員工價一律 STAFF_PRICE,不套用任何折扣
    2. 其餘情況依菜單單價 × 數量
    3. 會員且金額達 MEMBER_THRESHOLD 時打 MEMBER_RATE 折

    >>> line_price("珍珠奶茶", "大杯")
    65
    >>> line_price("珍珠奶茶", "大杯", 2)
    130
    >>> line_price("珍珠奶茶", "大杯", 4, is_member=True)
    234
    >>> line_price("珍珠奶茶", "大杯", 2, is_staff=True)
    80
    """
    if quantity <= 0:
        raise ValueError(f"數量必須大於 0，收到 {quantity}")

    if is_staff:
        return STAFF_PRICE * quantity

    amount = unit_price(name, size) * quantity
    if is_member:
        amount = apply_member_discount(amount)
    return amount
