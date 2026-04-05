import sys
from pathlib import Path

patch_src = Path(__file__).parent / "src"
sys.path.insert(0, str(patch_src))

print(f"Python path: {sys.path[:3]}")
print(f"Patch src: {patch_src}")

try:
    from copaw.app.channels.schema import BusMessage
    print("OK: BusMessage imported")
except Exception as e:
    print(f"FAIL: {e}")

try:
    from copaw.app.queue.sqlite_queue import SQLiteQueue
    print("OK: SQLiteQueue imported")
except Exception as e:
    print(f"FAIL: {e}")

try:
    from copaw.app.monitor.alerts import AlertManager
    print("OK: AlertManager imported")
except Exception as e:
    print(f"FAIL: {e}")
