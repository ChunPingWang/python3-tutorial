"""命令列介面 —— 這個套件裡唯一做「互動」的地方。

為什麼要把互動獨立成一個模組?

因為 input() / print() / sys.argv 都很難測試。
把它們集中在這裡,其他模組就能保持純函式,
而這個檔案本身幾乎沒有邏輯(只是把參數轉手傳給別人),所以不測也還好。

用法:

    python3 -m drinkshop.cli demo                 # 產生示範資料並印出日報表
    python3 -m drinkshop.cli demo --save 輸出     # 順便存檔
    python3 -m drinkshop.cli report 資料/2026-09  # 讀資料夾產生月報
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from drinkshop.menu import MENU
from drinkshop.orders import Order
from drinkshop.report import daily_report, monthly_summary, text_bar_chart
from drinkshop.storage import load_month, save_orders


def use_utf8_stdout() -> None:
    """讓 CLI 在 Windows 主控台也能印中文(見附錄 C)。

    🪟 Windows 的標準輸出預設不是 UTF-8,直接 print 中文會 UnicodeEncodeError。
    只在「做輸出的這一層」處理,其他模組完全不需要知道這件事。
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def make_demo_orders(on: date, count: int = 12, seed: int = 20260920) -> list[Order]:
    """產生示範訂單。

    亂數種子是參數而不是寫死的 —— 這樣測試可以要求「同樣種子給同樣結果」。
    """
    rng = random.Random(seed)
    items = list(MENU)
    return [
        Order(
            item=rng.choice(items),
            size=rng.choice(["中杯", "大杯"]),
            quantity=rng.randint(1, 3),
            is_member=rng.random() < 0.4,
            ordered_on=on,
        )
        for _ in range(count)
    ]


def cmd_demo(args: argparse.Namespace) -> int:
    today = date.today()
    orders = make_demo_orders(today, count=args.count, seed=args.seed)
    print(daily_report(orders, on=today))

    if args.save:
        path = save_orders(orders, Path(args.save) / f"{today.isoformat()}.csv")
        print(f"\n已存檔：{path}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"找不到資料夾：{folder}", file=sys.stderr)
        return 1

    by_day = load_month(folder)
    if not by_day:
        print(f"{folder} 裡沒有任何 .csv", file=sys.stderr)
        return 1

    summary = monthly_summary(by_day)
    print(f"{'月報表':^30}")
    print("=" * 34)
    print(text_bar_chart(summary))
    print("=" * 34)
    print(f"合計 {sum(summary.values()):,} 元，共 {len(summary)} 天")
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    """產生一整個月的示範資料,方便試玩 report 指令。"""
    folder = Path(args.folder)
    start = date.today() - timedelta(days=args.days - 1)
    for offset in range(args.days):
        day = start + timedelta(days=offset)
        orders = make_demo_orders(day, count=8 + offset % 5, seed=args.seed + offset)
        save_orders(orders, folder / f"{day.isoformat()}.csv")
    print(f"已在 {folder} 產生 {args.days} 天的示範資料")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drinkshop",
        description="阿宏手搖飲營運工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="產生示範訂單並印出日報表")
    demo.add_argument("--count", type=int, default=12, help="訂單筆數")
    demo.add_argument("--seed", type=int, default=20260920, help="亂數種子")
    demo.add_argument("--save", metavar="資料夾", help="順便把訂單存成 CSV")
    demo.set_defaults(func=cmd_demo)

    report = sub.add_parser("report", help="讀取資料夾裡的日報 CSV,產生月報")
    report.add_argument("folder", help="放 *.csv 的資料夾")
    report.set_defaults(func=cmd_report)

    seed = sub.add_parser("seed", help="產生一整個月的示範資料")
    seed.add_argument("folder", help="要寫入的資料夾")
    seed.add_argument("--days", type=int, default=7)
    seed.add_argument("--seed", type=int, default=20260920)
    seed.set_defaults(func=cmd_seed)

    return parser


def main(argv: list[str] | None = None) -> int:
    """進入點。argv 是參數而不是直接讀 sys.argv —— 這樣才測得動。"""
    use_utf8_stdout()
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
