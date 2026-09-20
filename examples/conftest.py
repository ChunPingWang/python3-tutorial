"""pytest 的設定檔。

它存在的理由只有一個:**讓 `tests/` 裡的測試找得到 `drinkshop` 套件**。

pytest 在收集測試時,會把「最上層 conftest.py 所在的目錄」加進 sys.path,
所以把這個檔案放在專案根目錄,就能直接在這裡執行:

    pytest

而不需要先 `pip install -e .`(當然,正式專案還是建議裝起來)。

如果你想把這個範例當成真正的專案使用:

    python3 -m pip install -e .
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
