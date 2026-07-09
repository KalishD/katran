import sqlite3
import json

DB_PATH = r'C:\Users\kalishd\.local\share\mimocode\mimocode.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# List tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("=== TABLES ===")
for r in c.fetchall():
    print(r[0])

# List sessions
print("\n=== SESSIONS ===")
c.execute("SELECT * FROM session ORDER BY time_created DESC")
cols = [d[0] for d in c.description]
for r in c.fetchall():
    row = dict(zip(cols, r))
    print(json.dumps(row, default=str, ensure_ascii=False))

# List checkpoint parts
print("\n=== CHECKPOINT PARTS (last 20) ===")
c.execute("""
    SELECT p.id, p.session_id, p.time_created, substr(p.data, 1, 500) as preview
    FROM part p
    WHERE json_extract(p.data, '$.type') = 'checkpoint'
    ORDER BY p.time_created DESC
    LIMIT 20
""")
for r in c.fetchall():
    print(dict(r))

conn.close()
