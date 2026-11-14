import json, sys, time
sys.path.insert(0, r"C:\Users\zsc\Desktop\independent project26-27fall")
from pathlib import Path
from factorlab.campaign import count_expressions
out = Path(r"C:\Users\zsc\Desktop\independent project26-27fall\experiments\20261114-systemv1-500")
log = out / "progress.log"
for _ in range(24):
    time.sleep(300)
    done = len(list(out.glob("*/evaluations.json")))
    line = time.strftime("%H:%M:%S") + f" expressions={count_expressions(out)} completed_runs={done}"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
