"""record.py TC-ID STATUS "actual result" [evidence,comma,separated] [DEF-x,DEF-y]"""
import json, sys, datetime, pathlib
p = pathlib.Path(__file__).with_name("results.json")
data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
tcid, status, actual = sys.argv[1], sys.argv[2], sys.argv[3]
assert status in ("Pass", "Fail", "Blocked", "Not Executed"), status
ev = [e for e in (sys.argv[4].split(",") if len(sys.argv) > 4 else []) if e]
defs = [d for d in (sys.argv[5].split(",") if len(sys.argv) > 5 else []) if d]
now = datetime.datetime.now()
data[tcid] = {"status": status, "actual": actual, "evidence": ev, "defects": defs,
              "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M")}
p.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{tcid} {status} recorded ({len(data)} total)")
