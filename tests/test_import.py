import sys
from pathlib import Path

patch_src = Path(__file__).parent / "src"
sys.path.insert(0, str(patch_src))

try:
    from copaw.app.channels.adapters.dingtalk import DingTalkAdapter
    print("[OK] DingTalkAdapter import OK")
except Exception as e:
    print(f"[FAIL] DingTalkAdapter import failed: {e}")

try:
    from copaw.app.channels.adapters.feishu import FeishuAdapter
    print("[OK] FeishuAdapter import OK")
except Exception as e:
    print(f"[FAIL] FeishuAdapter import failed: {e}")

try:
    from copaw.app.channels.base_v2 import BaseChannelV2
    print("[OK] BaseChannelV2 import OK")
except Exception as e:
    print(f"[FAIL] BaseChannelV2 import failed: {e}")
