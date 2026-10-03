import sqlite3
import json

DB_PATH = r'C:\Users\kalishd\.local\share\mimocode\mimocode.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Check the Distill session for skills created
SESSION_ID = 'ses_0de3e0b78ffetoh7j3b8TJKxg3'
print(f"=== SESSION shiny-eagle (Auto Distill) ===")
c.execute("""
    SELECT m.id, m.time_created,
           json_extract(m.data, '$.role') as role,
           json_extract(p.data, '$.type') as part_type,
           json_extract(p.data, '$.text') as text,
           json_extract(p.data, '$.tool') as tool
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE m.session_id = ?
    ORDER BY m.time_created, p.time_created
""", (SESSION_ID,))
for r in c.fetchall():
    row = dict(r)
    if row['part_type'] == 'text' and row['text']:
        role = row['role']
        text = row['text'][:200]
        print(f"[{role}] {text}")
    elif row['part_type'] == 'tool' and row['tool']:
        print(f"  TOOL: {row['tool']}")

# Also check all write tool calls across ALL sessions
print("\n=== All Write tool calls across all sessions ===")
c.execute("""
    SELECT m.session_id,
           json_extract(p.data, '$.state.input') as input_data
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('Write', 'write')
    ORDER BY m.time_created
""")
for r in c.fetchall():
    inp = r['input_data']
    if inp:
        try:
            inp_dict = json.loads(inp) if isinstance(inp, str) else inp
            if isinstance(inp_dict, dict):
                path = inp_dict.get('file_path', inp_dict.get('path', ''))
                print(f"  [{r['session_id'][:20]}] {path}")
        except:
            pass

# Check for actor registry (subagents)
print("\n=== Actor Registry ===")
c.execute("SELECT * FROM actor_registry")
cols = [d[0] for d in c.description] if c.description else []
for r in c.fetchall():
    row = dict(zip(cols, r)) if cols else dict(r)
    print(json.dumps(row, default=str, ensure_ascii=False)[:200])

# Check memory_fts for any previously consolidated memory
print("\n=== Memory FTS entries ===")
c.execute("SELECT COUNT(*) FROM memory_fts")
count = c.fetchone()[0]
print(f"  Total memory entries: {count}")

if count > 0:
    c.execute("SELECT * FROM memory_fts LIMIT 5")
    cols = [d[0] for d in c.description] if c.description else []
    for r in c.fetchall():
        row = dict(zip(cols, r)) if cols else dict(r)
        print(json.dumps(row, default=str, ensure_ascii=False)[:300])

conn.close()
