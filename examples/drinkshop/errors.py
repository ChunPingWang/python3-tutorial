"""這個套件會拋出的例外。

為什麼要自訂例外?因為呼叫方可以精準處理特定狀況:

    try:
        place_order(...)
    except OutOfStock:
        show("這個品項賣完了")      # 給客人友善訊息
    except MenuItemNotFound:
        log_bug()                  # 這是我們的問題

比起全部拋 ValueError 再用字串比對訊息,乾淨太多。
"""


class DrinkShopError(Exception):
    """這個套件所有例外的共同父類別。

    呼叫方可以用 `except DrinkShopError:` 一次接住全部,
    也可以分別處理下面的子類別。
    """


class MenuItemNotFound(DrinkShopError):
    """菜單上沒有這個品項或杯型。

    這通常代表點餐系統有 bug（讓客人點了不存在的東西），
    而不是正常的業務情境 —— 所以我們選擇拋出例外，而不是回傳 0。
    """


class OutOfStock(DrinkShopError):
    """庫存不足以完成這筆訂單。"""


class InvalidInput(DrinkShopError):
    """使用者輸入的資料不合法。"""
