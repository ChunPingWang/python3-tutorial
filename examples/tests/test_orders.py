"""orders 模組的測試。"""

from datetime import date

from drinkshop.errors import InvalidInput, OutOfStock
from drinkshop.orders import MAX_QUANTITY, Order, checkout, deduct_stock, parse_quantity


# --- Order：屬性與計算 ---

def test_訂單會自己算小計():
    assert Order("珍珠奶茶", "大杯", 2).subtotal == 130


def test_訂單會自己算應付金額():
    assert Order("珍珠奶茶", "大杯", 2).total == 130
    assert Order("珍珠奶茶", "大杯", 4, is_member=True).total == 234


def test_改了數量之後小計自動更新():
    order = Order("珍珠奶茶", "大杯")
    assert order.subtotal == 65
    order.quantity = 3
    assert order.subtotal == 195          # @property 是即時計算的


def test_預設是中杯一杯非會員():
    order = Order("珍珠奶茶")
    assert (order.size, order.quantity, order.is_member) == ("中杯", 1, False)


def test_內容相同的兩筆訂單相等():
    # dataclass 自動產生的 __eq__，讓斷言只要一行
    assert Order("珍珠奶茶", "大杯", 2) == Order("珍珠奶茶", "大杯", 2)


def test_內容不同的兩筆訂單不相等():
    assert Order("珍珠奶茶", "大杯", 2) != Order("珍珠奶茶", "中杯", 2)


def test_每筆訂單有自己的加料清單():
    """可變預設值陷阱的回歸測試（第 6 章）。"""
    a, b = Order("珍珠奶茶"), Order("紅茶拿鐵")
    a.toppings.append("珍珠")
    assert b.toppings == [], "兩筆訂單不該共用同一個清單"


def test_字串表示法看得懂():
    assert str(Order("珍珠奶茶", "大杯", 2)) == "珍珠奶茶(大杯) x2 = 130 元"


# --- parse_quantity：使用者輸入（錯誤處理是功能，也要測） ---

def test_正常的數字輸入():
    assert parse_quantity("2") == 2


def test_前後空白會被忽略():
    assert parse_quantity(" 3 ") == 3


def test_剛好等於上限可以接受():
    assert parse_quantity(str(MAX_QUANTITY)) == MAX_QUANTITY


def test_不合法的輸入一律拋出InvalidInput():
    bad_inputs = ["兩杯", "", "  ", "0", "-1", str(MAX_QUANTITY + 1), "3.5"]
    for raw in bad_inputs:
        try:
            parse_quantity(raw)
        except InvalidInput:
            continue
        raise AssertionError(f"{raw!r} 應該要被拒絕")


def test_錯誤訊息要告訴使用者怎麼改():
    try:
        parse_quantity("兩杯")
    except InvalidInput as exc:
        assert "數字" in str(exc)


# --- checkout ---

def test_結帳把多筆訂單加起來():
    orders = [Order("珍珠奶茶", "大杯"), Order("四季春茶", "中杯")]
    assert checkout(orders) == 95


def test_空訂單結帳是零而不是爆炸():
    assert checkout([]) == 0


def test_結帳可以含稅():
    orders = [Order("珍珠奶茶", "大杯", 3)]     # 195
    assert checkout(orders, include_tax=True) == 205


# --- deduct_stock ---

def test_扣庫存回傳新的字典():
    stock = {"珍珠奶茶": 5}
    after = deduct_stock(stock, "珍珠奶茶", 2)
    assert after == {"珍珠奶茶": 3}
    assert stock == {"珍珠奶茶": 5}, "不應該就地修改傳進來的字典"


def test_剛好扣完可以接受():
    assert deduct_stock({"珍珠奶茶": 2}, "珍珠奶茶", 2) == {"珍珠奶茶": 0}


def test_庫存不足要拋出OutOfStock():
    try:
        deduct_stock({"珍珠奶茶": 1}, "珍珠奶茶", 2)
    except OutOfStock as exc:
        assert "只剩 1 杯" in str(exc)
        return
    raise AssertionError("應該要拋出 OutOfStock")


def test_沒有庫存紀錄的品項視為零():
    try:
        deduct_stock({}, "珍珠奶茶", 1)
    except OutOfStock:
        return
    raise AssertionError("應該要拋出 OutOfStock")


def test_訂單可以記錄日期():
    order = Order("珍珠奶茶", ordered_on=date(2026, 9, 20))
    assert order.ordered_on == date(2026, 9, 20)
