#!/usr/bin/env python3
"""把 notebooks/src/*.py（percent 格式）轉成 notebooks/*.ipynb。

percent 格式說明（VS Code、PyCharm、jupytext 都認得）:

    # %% [markdown]
    # # 這是標題
    # 這是內文

    # %%
    print("這是程式碼 cell")

用法:
    python3 tools/build_notebooks.py          # 轉檔
    python3 tools/build_notebooks.py --check  # 轉檔後實際執行每個 notebook 驗證
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat


def use_utf8_stdout() -> None:
    """讓這支程式在 Windows 主控台也能印中文。

    🪟 Windows 的標準輸出預設不是 UTF-8(可能是 cp950 或 cp1252),
    直接 print 中文會得到:

        UnicodeEncodeError: 'charmap' codec can't encode characters...

    這不是你的程式邏輯有問題,是「輸出管道」的編碼問題。
    Python 3.7+ 可以直接把 stdout 重新設定成 UTF-8。
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


use_utf8_stdout()

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "notebooks" / "src"
OUT_DIR = ROOT / "notebooks"


def parse_cells(text: str) -> list[tuple[str, str]]:
    """把 percent 格式文字切成 [(cell_type, source), ...]。"""
    cells: list[tuple[str, str]] = []
    cell_type = "code"
    buffer: list[str] = []

    def flush() -> None:
        source = "\n".join(buffer).strip("\n")
        if source.strip():
            cells.append((cell_type, source))
        buffer.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# %%"):
            flush()
            cell_type = "markdown" if "[markdown]" in stripped else "code"
            continue
        if cell_type == "markdown":
            # markdown cell 的每一行都以 "# " 開頭，去掉它
            if line.startswith("# "):
                buffer.append(line[2:])
            elif stripped == "#":
                buffer.append("")
            else:
                buffer.append(line)
        else:
            buffer.append(line)
    flush()
    return cells


def build(src: Path) -> Path:
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python"}
    for index, (cell_type, source) in enumerate(parse_cells(src.read_text(encoding="utf-8"))):
        if cell_type == "markdown":
            cell = nbformat.v4.new_markdown_cell(source)
        else:
            cell = nbformat.v4.new_code_cell(source)
        # nbformat 預設給每個 cell 一個隨機 id,那會讓每次重建的檔案都不一樣,
        # git diff 因此充滿雜訊。改成依順序的固定 id,同樣的來源就產生同樣的檔案。
        cell["id"] = f"c{index:03d}"
        nb.cells.append(cell)

    out = OUT_DIR / (src.stem + ".ipynb")
    nbformat.write(nb, out)
    return out


def check(path: Path) -> None:
    """實際執行 notebook,確保教材裡的程式碼真的跑得動。"""
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(OUT_DIR)}},
    )
    client.execute()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(SRC_DIR.glob("*.py"))
    if not sources:
        print(f"找不到任何來源檔:{SRC_DIR}")
        return 1

    failed = []
    for src in sources:
        out = build(src)
        print(f"[build] {src.name} -> {out.relative_to(ROOT)}")
        if "--check" in sys.argv:
            try:
                check(out)
                print(f"[ ok  ] {out.name} 執行成功")
            except Exception as exc:  # noqa: BLE001 - 這裡就是要把所有錯誤攤開
                failed.append((out.name, exc))
                print(f"[FAIL ] {out.name}: {type(exc).__name__}: {exc}")

    if failed:
        print(f"\n{len(failed)} 個 notebook 執行失敗")
        return 1
    print(f"\n完成,共 {len(sources)} 個 notebook。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
