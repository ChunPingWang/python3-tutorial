"""pricing 模組的測試。

這些測試刻意寫成「純函式 + assert」,所以

    pytest                  ← 有裝 pytest 的話
    python3 run_tests.py    ← 沒裝也能跑

兩種方式都能執行。測試名稱用中文描述**行為**,
把它們列出來就是一份規格書。
"""

from drinkshop.errors import MenuItemNotFound
from drinkshop.pricing import (
    MEMBER_THRESHOLD,
    apply_member_discount,
    line_price,
    round_half_up,
    unit_price,
    with_tax,
)


# --- round_half_up：台灣式四捨五入 ---

def test_逢五進一而不是銀行家捨入():
    # Python 內建 round(2.5) == 2，阿宏會覺得算錯
    assert round_half_up(2.5) == 3
    assert round_half_up(0.5) == 1
    assert round_half_up(58.5) == 59


def test_不到五捨去():
    assert round_half_up(2.4) == 2
    assert round_half_up(204.4) == 204


def test_零和整數維持不變():
    assert round_half_up(0) == 0
    assert round_half_up(65) == 65


def test_負數也照逢五進一():
    assert round_half_up(-2.5) == -3


# --- unit_price：查價 ---

def test_查得到菜單上的價格():
    assert unit_price("珍珠奶茶", "大杯") == 65
    assert unit_price("珍珠奶茶", "中杯") == 55


def test_品項不存在要拋出MenuItemNotFound():
    try:
        unit_price("綠茶", "大杯")
    except MenuItemNotFound:
        return
    raise AssertionError("應該要拋出 MenuItemNotFound")


def test_杯型不存在要拋出MenuItemNotFound():
    try:
        unit_price("珍珠奶茶", "特大杯")
    except MenuItemNotFound:
        return
    raise AssertionError("應該要拋出 MenuItemNotFound")


def test_錯誤訊息要說清楚是哪個品項():
    try:
        unit_price("綠茶", "大杯")
    except MenuItemNotFound as exc:
        assert "綠茶" in str(exc)


# --- apply_member_discount：滿額才打折（邊界重點） ---

def test_未達門檻不打折():
    assert apply_member_discount(MEMBER_THRESHOLD - 1) == MEMBER_THRESHOLD - 1


def test_剛好達到門檻就打折():
    assert apply_member_discount(MEMBER_THRESHOLD) == 180


def test_超過門檻打折():
    assert apply_member_discount(500) == 450


def test_金額為零也不會出事():
    assert apply_member_discount(0) == 0


# --- with_tax ---

def test_含稅金額四捨五入到整數():
    # 195 * 1.05 = 204.75 → 205
    assert with_tax(195) == 205
    assert with_tax(100) == 105
    assert with_tax(0) == 0


# --- line_price：把規則組合起來 ---

def test_一般客人依菜單計價():
    assert line_price("珍珠奶茶", "大杯") == 65
    assert line_price("珍珠奶茶", "大杯", 2) == 130


def test_會員未滿門檻不打折():
    # 65 * 2 = 130 < 200
    assert line_price("珍珠奶茶", "大杯", 2, is_member=True) == 130


def test_會員滿門檻才打折():
    # 65 * 4 = 260 → 234
    assert line_price("珍珠奶茶", "大杯", 4, is_member=True) == 234


def test_員工價蓋過一切折扣():
    assert line_price("珍珠奶茶", "大杯", 2, is_staff=True) == 80
    assert line_price("珍珠奶茶", "大杯", 2, is_member=True, is_staff=True) == 80


def test_數量為零或負數要被拒絕():
    for bad in (0, -1):
        try:
            line_price("珍珠奶茶", "大杯", bad)
        except ValueError:
            continue
        raise AssertionError(f"數量 {bad} 應該要被拒絕")


def test_所有品項與杯型的組合都算得出價格():
    """參數化的精神：一個測試涵蓋多組案例。

    pytest 使用者可以改用 @pytest.mark.parametrize，
    報表會把每一組列成獨立的測試。
    """
    cases = [
        ("珍珠奶茶", "中杯", 55),
        ("珍珠奶茶", "大杯", 65),
        ("冬瓜檸檬", "中杯", 40),
        ("冬瓜檸檬", "大杯", 45),
        ("四季春茶", "中杯", 30),
        ("黑糖鮮奶", "大杯", 70),
    ]
    for name, size, expected in cases:
        assert line_price(name, size) == expected, f"{name} {size} 應該是 {expected}"
