"""Full gate: unittest baseline plus complete pytest suite; run from repository root."""
import subprocess
import sys
import unittest
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
suite=unittest.defaultTestLoader.discover(str(root/'tests'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
# pytest discovers the unittest suite plus pytest-style functions (42 + 30).
# A missing/broken pytest install must fail the gate, never pass it.
proc=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=str(root),check=False)
raise SystemExit(proc.returncode)

