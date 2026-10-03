import sqlite3
import json

DB_PATH = r'C:\Users\kalishd\.local\share\mimocode\mimocode.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Get all project sessions (not subagents), ordered by time
print("=== ALL PROJECT SESSIONS ===")
c.execute("""
    SELECT id, slug, title, time_created, time_updated, parent_id
    FROM session
    WHERE project_id = 'f262ed33-d7b2-4021-9abf-6610a8eaa37c'
    ORDER BY time_created ASC
""")
for r in c.fetchall():
    row = dict(r)
    print(f"{row['id']} | {row['slug']} | {row['title'][:80]} | parent={row['parent_id']}")

# Count messages per session
print("\n=== MESSAGE COUNT PER SESSION ===")
c.execute("""
    SELECT session_id, COUNT(*) as msg_count
    FROM message
    GROUP BY session_id
    ORDER BY msg_count DESC
""")
for r in c.fetchall():
    print(dict(r))

# Look at parts - what types exist?
print("\n=== PART TYPES ===")
c.execute("""
    SELECT json_extract(p.data, '$.type') as part_type, COUNT(*) as cnt
    FROM part p
    GROUP BY part_type
    ORDER BY cnt DESC
""")
for r in c.fetchall():
    print(dict(r))

# Check for todo items
print("\n=== TODO ITEMS ===")
c.execute("SELECT * FROM todo")
cols = [d[0] for d in c.description]
for r in c.fetchall():
    row = dict(zip(cols, r))
    print(json.dumps(row, default=str, ensure_ascii=False)[:200])

# Check tasks
print("\n=== TASKS ===")
c.execute("SELECT * FROM task")
cols = [d[0] for d in c.description]
for r in c.fetchall():
    row = dict(zip(cols, r))
    print(json.dumps(row, default=str, ensure_ascii=False)[:200])

conn.close()
