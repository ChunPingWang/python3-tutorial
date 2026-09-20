"""訂單模型與結帳邏輯。

Order 用 dataclass:自動產生 __init__、__repr__、__eq__,
最後一個對測試特別重要 —— 一行 assert 就能比對整筆訂單。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from drinkshop.errors import InvalidInput, OutOfStock
from drinkshop.pricing import line_price, unit_price, with_tax

MAX_QUANTITY = 50


@dataclass
class Order:
    """一筆訂單。

    >>> o = Order("珍珠奶茶", "大杯", 2)
    >>> o.subtotal
    130
    >>> Order("珍珠奶茶", "大杯", 4, is_member=True).total
    234
    """

    item: str
    size: str = "中杯"
    quantity: int = 1
    is_member: bool = False
    is_staff: bool = False
    note: str = ""
    toppings: list[str] = field(default_factory=list)  # ⚠️ 可變預設值要這樣寫
    ordered_on: date | None = None

    @property
    def unit(self) -> int:
        """單價(不含折扣)。"""
        return unit_price(self.item, self.size)

    @property
    def subtotal(self) -> int:
        """數量 × 單價,未套用折扣。"""
        return self.unit * self.quantity

    @property
    def total(self) -> int:
        """實際應付金額(含員工價與會員折扣)。"""
        return line_price(
            self.item,
            self.size,
            self.quantity,
            is_member=self.is_member,
            is_staff=self.is_staff,
        )

    def __str__(self) -> str:
        return f"{self.item}({self.size}) x{self.quantity} = {self.total} 元"


def parse_quantity(raw: str) -> int:
    """把使用者輸入的文字轉成數量。

    這是一個「純函式」:只負責判斷和拋錯,不做任何互動。
    互動(input / print)留給 cli.py —— 這樣這個函式才測得動。

    >>> parse_quantity("2")
    2
    >>> parse_quantity(" 3 ")
    3
    """
    text = raw.strip()
    try:
        quantity = int(text)
    except ValueError as exc:
        raise InvalidInput(f"數量請輸入數字，你輸入的是「{text}」") from exc

    if quantity <= 0:
        raise InvalidInput(f"數量必須大於 0，你輸入的是 {quantity}")
    if quantity > MAX_QUANTITY:
        raise InvalidInput(f"單筆最多 {MAX_QUANTITY} 杯，你輸入的是 {quantity}")
    return quantity


def checkout(orders: list[Order], *, include_tax: bool = False) -> int:
    """結帳:把多筆訂單加總。

    >>> checkout([Order("珍珠奶茶", "大杯"), Order("四季春茶", "中杯")])
    95
    >>> checkout([])
    0
    """
    total = sum(order.total for order in orders)
    return with_tax(total) if include_tax else total


def deduct_stock(stock: dict[str, int], item: str, quantity: int) -> dict[str, int]:
    """扣庫存,回傳**新的**庫存字典(不改動傳進來的那個)。

    不就地修改參數,是讓函式好測試、好推理的重要習慣:
    呼叫它不會在你背後偷偷改掉別人的資料。

    >>> deduct_stock({"珍珠奶茶": 5}, "珍珠奶茶", 2)
    {'珍珠奶茶': 3}
    """
    remaining = stock.get(item, 0)
    if remaining < quantity:
        raise OutOfStock(f"{item} 只剩 {remaining} 杯，你要 {quantity} 杯")
    return {**stock, item: remaining - quantity}
