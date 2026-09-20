#!/usr/bin/env python3
"""不需要安裝 pytest 的測試執行器。

寫這個檔案有兩個目的:

1. **讓沒裝 pytest 的人也能跑完整的測試套件**(教學現場很常見)
2. **讓你看見 pytest 的核心其實很簡單**:
   找出名字以 `test_` 開頭的函式,一個一個呼叫,統計結果。

   pytest 多做的是:漂亮的報表、assert 拆解、fixture、參數化、外掛生態系。
   但骨架就是下面這 40 行。

用法:

    python3 run_tests.py            # 跑全部
    python3 run_tests.py 會員        # 只跑名字含「會員」的（相當於 pytest -k）
    python3 run_tests.py --doctest  # 順便跑所有 docstring 裡的範例
"""

from __future__ import annotations

import doctest
import importlib
import sys
import traceback
from pathlib import Path


def use_utf8_stdout() -> None:
    """讓這支程式在 Windows 主控台也能印中文(見附錄 C)。

    🪟 Windows 的標準輸出預設不是 UTF-8,直接 print 中文會得到

        UnicodeEncodeError: 'charmap' codec can't encode characters...

    這不是程式邏輯有問題,是「輸出管道」的編碼問題。
    這個專案的 CI 第一次在 Windows 上跑的時候,就是死在這裡。
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


use_utf8_stdout()

ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def collect_modules() -> list:
    """匯入 tests/ 底下所有 test_*.py。"""
    sys.path.insert(0, str(TESTS_DIR))
    return [
        importlib.import_module(path.stem)
        for path in sorted(TESTS_DIR.glob("test_*.py"))
    ]


def run_tests(keyword: str | None = None) -> tuple[int, int]:
    passed = failed = 0

    for module in collect_modules():
        names = [n for n in dir(module) if n.startswith("test_")]
        if keyword:
            names = [n for n in names if keyword in n]
        if not names:
            continue

        print(f"\n{module.__name__}")
        for name in names:
            try:
                getattr(module, name)()
            except AssertionError as exc:
                failed += 1
                print(f"  🔴 {name}")
                print(f"     {exc or '斷言失敗'}")
            except Exception:  # noqa: BLE001 - 測試執行器就是要攤開所有錯誤
                failed += 1
                print(f"  🔴 {name}（執行時發生例外）")
                print("     " + traceback.format_exc().strip().replace("\n", "\n     "))
            else:
                passed += 1
                print(f"  🟢 {name}")

    return passed, failed


def run_doctests() -> tuple[int, int]:
    """執行 drinkshop 套件裡所有 docstring 中的範例。"""
    import drinkshop
    from drinkshop import menu, orders, pricing, report

    attempted = failed = 0
    for module in (drinkshop, menu, pricing, orders, report):
        result = doctest.testmod(module, verbose=False)
        attempted += result.attempted
        failed += result.failed
    return attempted, failed


def main(argv: list[str]) -> int:
    keyword = next((a for a in argv if not a.startswith("-")), None)

    print("=" * 52)
    print("  drinkshop 測試套件（不需要 pytest）")
    print("=" * 52)

    passed, failed = run_tests(keyword)

    print("\n" + "-" * 52)
    print(f"測試：共 {passed + failed} 個，🟢 通過 {passed}，🔴 失敗 {failed}")

    if "--doctest" in argv:
        attempted, doc_failed = run_doctests()
        print(f"doctest：共 {attempted} 個範例，🔴 失敗 {doc_failed}")
        failed += doc_failed

    print("-" * 52)
    if failed:
        print("\n有測試沒過。修好之後再跑一次。")
        return 1

    print("\n全部通過 🎉")
    print("（有裝 pytest 的話，直接執行 `pytest -v` 會得到更漂亮的報表）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
