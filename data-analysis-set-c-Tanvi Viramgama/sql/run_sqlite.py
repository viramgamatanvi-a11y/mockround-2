"""Helper: runs sql/setup.sql then sql/queries.sql on a fresh SQLite DB and
saves every labeled query result into outputs/sql/.  Run from the repo root:
    python sql/run_sqlite.py
(Examiner can alternatively run the two .sql files manually in any SQLite client.)"""
import csv, re, sqlite3
from pathlib import Path

OUT = Path("outputs/sql"); OUT.mkdir(parents=True, exist_ok=True)
FILES = {
    "S2a":   "s2a_avg_score_by_department.csv",
    "S2b":   "s2b_underperforming_courses.csv",
    "S2c":   "s2c_top_two_batches.csv",
    "S3_D1": "s3_integrity_courses_left_join.csv",
    "S3_D2": "s3_integrity_unmatched_keys.csv",
}

con = sqlite3.connect(":memory:")
con.executescript(Path("sql/setup.sql").read_text(encoding="utf-8"))
print("SQLite version:", sqlite3.sqlite_version)

text = Path("sql/queries.sql").read_text(encoding="utf-8")
parts = re.split(r"^-- \[(\w+)\].*$", text, flags=re.M)
for label, body in zip(parts[1::2], parts[2::2]):
    sql = "\n".join(l for l in body.splitlines() if not l.strip().startswith("--")).strip()
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with open(OUT / FILES[label], "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(rows)
    print(f"\n[{label}] -> {FILES[label]}")
    print(cols)
    for r in rows:
        print(r)
