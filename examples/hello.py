"""最小的可執行範例 —— 確認你的環境是好的。

執行方式:

    python3 hello.py        # 🍎🐧
    py -3 hello.py          # 🪟
"""

import platform
import sys


def greet(name: str = "世界") -> str:
    """回傳打招呼的字串。

    注意它是 return 而不是 print —— 這樣才測得動(第 6 章)。

    >>> greet()
    '哈囉，世界！'
    >>> greet("阿宏")
    '哈囉，阿宏！'
    """
    return f"哈囉，{name}！"


def main() -> None:
    print(greet())
    print(f"Python {sys.version.split()[0]} on {platform.system()}")
    print(f"執行檔：{sys.executable}")

    # 你的第一個測試
    assert greet("阿宏") == "哈囉，阿宏！"
    print("🟢 自我檢查通過")


if __name__ == "__main__":
    main()
