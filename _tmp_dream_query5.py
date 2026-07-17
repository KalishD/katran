import sqlite3
import json

DB_PATH = r'C:\Users\kalishd\.local\share\mimocode\mimocode.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Get all tool calls with write/edit from brave-harbor
SESSION_ID = 'ses_0de40df4effephtIr84xUCQODA'
print(f"=== brave-harbor: All Write/Edit tool calls ===")
c.execute("""
    SELECT m.id, m.time_created,
           json_extract(p.data, '$.tool') as tool,
           json_extract(p.data, '$.state.input') as input_data,
           substr(json_extract(p.data, '$.state.output'), 1, 200) as output_preview
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE m.session_id = ?
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('Write', 'Edit', 'write', 'edit')
    ORDER BY m.time_created, p.time_created
""", (SESSION_ID,))
for r in c.fetchall():
    row = dict(r)
    inp = row.get('input_data', '')
    if inp:
        try:
            inp_dict = json.loads(inp) if isinstance(inp, str) else inp
            if isinstance(inp_dict, dict):
                path = inp_dict.get('file_path', inp_dict.get('path', ''))
                print(f"  {row['tool']}: {path}")
                if row['tool'] in ('Edit', 'edit') and 'old_string' in inp_dict:
                    old = inp_dict['old_string'][:80]
                    new = inp_dict['new_string'][:80]
                    print(f"    OLD: {old}")
                    print(f"    NEW: {new}")
        except:
            pass

# Search for user rules/decisions in ALL sessions
print("\n=== User statements containing 'всегда', 'никогда', 'важно', 'решение' ===")
c.execute("""
    SELECT m.session_id,
           json_extract(m.data, '$.role') as role,
           json_extract(p.data, '$.text') as text
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'user'
      AND json_extract(p.data, '$.type') = 'text'
      AND (
          json_extract(p.data, '$.text') LIKE '%всегда%'
          OR json_extract(p.data, '$.text') LIKE '%никогда%'
          OR json_extract(p.data, '$.text') LIKE '%важно%'
          OR json_extract(p.data, '$.text') LIKE '%правило%'
          OR json_extract(p.data, '$.text') LIKE '%правила%'
          OR json_extract(p.data, '$.text') LIKE '%решение%'
          OR json_extract(p.data, '$.text') LIKE '%decided%'
          OR json_extract(p.data, '$.text') LIKE '%always%'
          OR json_extract(p.data, '$.text') LIKE '%never%'
          OR json_extract(p.data, '$.text') LIKE '%remember%'
          OR json_extract(p.data, '$.text') LIKE '%rule%'
          OR json_extract(p.data, '$.text') LIKE '%ошибк%'
          OR json_extract(p.data, '$.text') LIKE '%не ищи%'
      )
    ORDER BY m.time_created
""")
for r in c.fetchall():
    row = dict(r)
    text = row['text'][:300] if row['text'] else ''
    print(f"  [{row['session_id'][:20]}] {text}")

# Check for repeated error patterns
print("\n=== Repeated error patterns in tool outputs ===")
c.execute("""
    SELECT json_extract(p.data, '$.state.output') as output
    FROM part p
    WHERE json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.state.output') LIKE '%error%'
      AND json_extract(p.data, '$.state.output') LIKE '%Error%'
    LIMIT 10
""")
for r in c.fetchall():
    output = r['output'][:200] if r['output'] else ''
    print(f"  {output}")

# Check task events for any tracked tasks
print("\n=== Task Events ===")
c.execute("SELECT * FROM task_event")
cols = [d[0] for d in c.description] if c.description else []
for r in c.fetchall():
    row = dict(zip(cols, r)) if cols else dict(r)
    print(json.dumps(row, default=str, ensure_ascii=False)[:200])

conn.close()
