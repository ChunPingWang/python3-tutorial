"""report 模組的測試。

注意每個測試都自己建立資料,而且日期是寫死的常數 ——
**測試絕對不可以依賴「今天是幾號」**,否則它今天過、下週掛。
"""

from datetime import date

from drinkshop.orders import Order
from drinkshop.report import (
    average_ticket,
    cup_count,
    cups_by_item,
    daily_report,
    median_ticket,
    member_ratio,
    monthly_summary,
    revenue,
    revenue_by_item,
    slow_movers,
    text_bar_chart,
    top_items,
)

REPORT_DAY = date(2026, 9, 20)          # 週日，固定值，測試才可重現


def sample_orders() -> list[Order]:
    """每個測試呼叫它拿到一份全新的資料，避免測試互相影響。"""
    return [
        Order("珍珠奶茶", "大杯", 2),          # 130
        Order("珍珠奶茶", "中杯", 1),          # 55
        Order("四季春茶", "中杯", 3),          # 90
        Order("冬瓜檸檬", "大杯", 1, is_member=True),   # 45（未達門檻不打折）
    ]


# --- 基本統計 ---

def test_總營收():
    assert revenue(sample_orders()) == 320


def test_總杯數是把數量加起來而不是筆數():
    assert cup_count(sample_orders()) == 7
    assert len(sample_orders()) == 4


def test_空訂單的營收是零():
    assert revenue([]) == 0
    assert cup_count([]) == 0


def test_平均客單價():
    assert average_ticket(sample_orders()) == 80       # 320 / 4


def test_空訂單的平均是零而不是除以零錯誤():
    """打烊時如果一筆訂單都沒有，日報表不該掛掉。"""
    assert average_ticket([]) == 0
    assert median_ticket([]) == 0


def test_中位數不會被團購拉走():
    orders = [
        Order("四季春茶", "中杯"),              # 30
        Order("珍珠奶茶", "中杯"),              # 55
        Order("珍珠奶茶", "大杯", 20),          # 1300 團購
    ]
    assert average_ticket(orders) == 462        # 被拉高了
    assert median_ticket(orders) == 55          # 中位數比較真實


def test_會員佔比():
    assert member_ratio(sample_orders()) == 0.25
    assert member_ratio([]) == 0.0


# --- 分組統計 ---

def test_每個品項的營收():
    assert revenue_by_item(sample_orders()) == {
        "珍珠奶茶": 185,
        "四季春茶": 90,
        "冬瓜檸檬": 45,
    }


def test_每個品項的杯數():
    assert dict(cups_by_item(sample_orders())) == {
        "珍珠奶茶": 3,
        "四季春茶": 3,
        "冬瓜檸檬": 1,
    }


def test_熱銷排行取前兩名():
    ranking = top_items(sample_orders(), 2)
    assert len(ranking) == 2
    assert ranking[0][1] == 3          # 第一名賣了 3 杯


def test_沒有訂單時排行榜是空的():
    assert top_items([], 3) == []


# --- 滯銷品 ---

def test_滯銷品是菜單有但今天沒賣的():
    orders = [Order("珍珠奶茶")]
    idle = slow_movers(orders, catalog=["珍珠奶茶", "紅茶拿鐵", "四季春茶"])
    assert idle == {"紅茶拿鐵", "四季春茶"}


def test_全部都賣出時沒有滯銷品():
    catalog = ["珍珠奶茶", "四季春茶"]
    orders = [Order("珍珠奶茶"), Order("四季春茶")]
    assert slow_movers(orders, catalog=catalog) == set()


def test_沒有訂單時整份菜單都是滯銷品():
    catalog = ["珍珠奶茶", "四季春茶"]
    assert slow_movers([], catalog=catalog) == set(catalog)


# --- 日報表（測「內容包含什麼」，不要整份字串比對） ---

def test_日報表包含關鍵數字():
    text = daily_report(sample_orders(), on=REPORT_DAY)
    assert "320" in text
    assert "2026-09-20" in text
    assert "週日" in text
    assert "珍珠奶茶" in text


def test_沒有訂單也能產出報表而不是崩潰():
    text = daily_report([], on=REPORT_DAY)
    assert "今天沒有訂單" in text
    assert "0" in text


def test_日報表的星期名稱不受系統語系影響():
    """strftime('%A') 會因系統語系而異，所以我們自己做對照表。"""
    assert "週一" in daily_report([], on=date(2026, 9, 21))
    assert "週六" in daily_report([], on=date(2026, 9, 19))


# --- 月報 ---

def test_月報把每天的營收整理出來():
    by_day = {
        "2026-09-20": sample_orders(),
        "2026-09-19": [Order("珍珠奶茶", "大杯")],
    }
    assert monthly_summary(by_day) == {"2026-09-19": 65, "2026-09-20": 320}


def test_月報按日期排序():
    by_day = {"2026-09-20": [], "2026-09-01": [], "2026-09-10": []}
    assert list(monthly_summary(by_day)) == ["2026-09-01", "2026-09-10", "2026-09-20"]


def test_空月報是空字典():
    assert monthly_summary({}) == {}


# --- 文字長條圖（不需要 matplotlib，所以測得動） ---

def test_文字長條圖的最大值佔滿寬度():
    chart = text_bar_chart({"a": 10, "b": 5}, width=10)
    lines = chart.splitlines()
    assert lines[0].count("█") == 10
    assert lines[1].count("█") == 5


def test_沒有資料時給提示而不是崩潰():
    assert text_bar_chart({}) == "（沒有資料）"


def test_全部為零也不會除以零():
    assert "0" in text_bar_chart({"a": 0, "b": 0})
