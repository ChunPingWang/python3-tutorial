"""報表 —— 全部都是純函式,不碰檔案、不看時鐘。

需要「今天」的時候一律當成參數傳進來(見 daily_report 的 on 參數),
這樣測試才不會今天過、明天掛。
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from datetime import date

from drinkshop.menu import item_names
from drinkshop.orders import Order

WEEKDAY_NAMES = ("週一", "週二", "週三", "週四", "週五", "週六", "週日")


def revenue(orders: list[Order]) -> int:
    """總營收。

    >>> revenue([])
    0
    """
    return sum(order.total for order in orders)


def cup_count(orders: list[Order]) -> int:
    """總杯數(注意:一筆訂單可能好幾杯)。"""
    return sum(order.quantity for order in orders)


def average_ticket(orders: list[Order]) -> int:
    """平均客單價;沒有訂單時回傳 0(而不是 ZeroDivisionError)。

    >>> average_ticket([])
    0
    """
    if not orders:
        return 0
    return round(revenue(orders) / len(orders))


def median_ticket(orders: list[Order]) -> int:
    """中位數客單價。

    平均數會被團購那種極端值拉走,中位數不會 —— 阿宏要看的是這個。
    """
    if not orders:
        return 0
    return round(statistics.median(order.total for order in orders))


def revenue_by_item(orders: list[Order]) -> dict[str, int]:
    """每個品項的營收。"""
    result: dict[str, int] = defaultdict(int)
    for order in orders:
        result[order.item] += order.total
    return dict(result)


def cups_by_item(orders: list[Order]) -> Counter:
    """每個品項賣出的杯數。"""
    counter: Counter = Counter()
    for order in orders:
        counter[order.item] += order.quantity
    return counter


def top_items(orders: list[Order], n: int = 3) -> list[tuple[str, int]]:
    """熱銷排行榜(依杯數)。

    >>> top_items([], 3)
    []
    """
    return cups_by_item(orders).most_common(n)


def slow_movers(orders: list[Order], catalog: list[str] | None = None) -> set[str]:
    """完全沒賣出的品項(滯銷品)。

    用集合的差集,一行就算完,不用寫迴圈。
    """
    catalog = catalog if catalog is not None else item_names()
    return set(catalog) - {order.item for order in orders}


def member_ratio(orders: list[Order]) -> float:
    """會員訂單佔比(0.0 ~ 1.0)。"""
    if not orders:
        return 0.0
    return sum(1 for o in orders if o.is_member) / len(orders)


def daily_report(orders: list[Order], on: date) -> str:
    """產生一天的文字報表。

    注意 `on` 是參數而不是 date.today() —— 這樣測試永遠可重現。
    """
    lines = [
        "=" * 34,
        f"{'阿宏手搖飲 日報表':^28}",
        f"{on.isoformat()}（{WEEKDAY_NAMES[on.weekday()]}）".center(30),
        "=" * 34,
        f"{'總營收':<12}{revenue(orders):>10,} 元",
        f"{'總杯數':<12}{cup_count(orders):>10,} 杯",
        f"{'訂單筆數':<11}{len(orders):>10,} 筆",
        f"{'平均客單價':<10}{average_ticket(orders):>10,} 元",
        f"{'中位數客單價':<9}{median_ticket(orders):>10,} 元",
        f"{'會員佔比':<11}{member_ratio(orders):>10.0%}",
        "-" * 34,
        f"{'熱銷排行':<12}",
    ]

    ranking = top_items(orders, 3)
    if ranking:
        for i, (name, cups) in enumerate(ranking, start=1):
            lines.append(f"  {i}. {name:<10}{cups:>4} 杯")
    else:
        lines.append("  （今天沒有訂單）")

    idle = slow_movers(orders)
    if idle:
        lines += ["-" * 34, f"滯銷品項：{'、'.join(sorted(idle))}"]

    lines.append("=" * 34)
    return "\n".join(lines)


def monthly_summary(by_day: dict[str, list[Order]]) -> dict[str, int]:
    """把 {日期: 訂單清單} 整理成 {日期: 當日營收}。

    >>> monthly_summary({})
    {}
    """
    return {day: revenue(orders) for day, orders in sorted(by_day.items())}


def text_bar_chart(data: dict[str, int], width: int = 24) -> str:
    """純文字長條圖 —— 不需要 matplotlib,而且好測試。

    >>> print(text_bar_chart({"a": 1, "b": 2}, width=2))
    a  █ 1
    b  ██ 2
    """
    if not data:
        return "（沒有資料）"
    largest = max(data.values()) or 1
    return "\n".join(
        f"{label}  {'█' * round(value / largest * width)} {value:,}"
        for label, value in data.items()
    )
