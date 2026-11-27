import runpy
import sys
from pathlib import Path

import debugpy


port = int(sys.argv[1])
script = sys.argv[2]
arguments = sys.argv[3:]

print("DEBUGPY_STARTING", flush=True)
debugpy.listen(("127.0.0.1", port))
print("DEBUGPY_READY", flush=True)
debugpy.wait_for_client()

sys.argv = [script, *arguments]
sys.path.insert(0, str(Path(script).resolve().parent))
runpy.run_path(script, run_name="__main__")
