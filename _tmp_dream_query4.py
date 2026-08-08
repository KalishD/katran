import sqlite3
import json

DB_PATH = r'C:\Users\kalishd\.local\share\mimocode\mimocode.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Session: hidden-falcon (AGENTS.md creation)
SESSION_ID = 'ses_0de3e0bd9ffeVXArlImzGALo1T'
print(f"=== SESSION hidden-falcon (AGENTS.md) ===")
c.execute("""
    SELECT m.id, 
           json_extract(m.data, '$.role') as role,
           json_extract(p.data, '$.type') as part_type,
           json_extract(p.data, '$.text') as text,
           json_extract(p.data, '$.tool') as tool,
           substr(
               CASE 
                   WHEN json_extract(p.data, '$.type') = 'tool' 
                   THEN json_extract(p.data, '$.state.output')
                   ELSE NULL
               END, 1, 300
           ) as tool_output_preview
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE m.session_id = ?
    ORDER BY m.time_created, p.time_created
""", (SESSION_ID,))
for r in c.fetchall():
    row = dict(r)
    if row['part_type'] == 'text' and row['text']:
        role = row['role']
        text = row['text'][:300]
        print(f"[{role}] {text}")
    elif row['part_type'] == 'tool' and row['tool']:
        print(f"  TOOL: {row['tool']} -> {str(row.get('tool_output_preview', ''))[:150]}")

# Session: eager-island (Title request)
SESSION_ID = 'ses_0de3e0bccffeUzh54WdCDuRv0M'
print(f"\n=== SESSION eager-island (Title request) ===")
c.execute("""
    SELECT m.id, 
           json_extract(m.data, '$.role') as role,
           json_extract(p.data, '$.type') as part_type,
           json_extract(p.data, '$.text') as text,
           json_extract(p.data, '$.tool') as tool,
           substr(
               CASE 
                   WHEN json_extract(p.data, '$.type') = 'tool' 
                   THEN json_extract(p.data, '$.state.output')
                   ELSE NULL
               END, 1, 300
           ) as tool_output_preview
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE m.session_id = ?
    ORDER BY m.time_created, p.time_created
""", (SESSION_ID,))
for r in c.fetchall():
    row = dict(r)
    if row['part_type'] == 'text' and row['text']:
        role = row['role']
        text = row['text'][:300]
        print(f"[{role}] {text}")
    elif row['part_type'] == 'tool' and row['tool']:
        print(f"  TOOL: {row['tool']} -> {str(row.get('tool_output_preview', ''))[:150]}")

# Session: eager-wolf (Project map)
SESSION_ID = 'ses_0de40e04fffedgl76LW5QTloUv'
print(f"\n=== SESSION eager-wolf (Project map) ===")
c.execute("""
    SELECT m.id, 
           json_extract(m.data, '$.role') as role,
           json_extract(p.data, '$.type') as part_type,
           json_extract(p.data, '$.text') as text,
           json_extract(p.data, '$.tool') as tool,
           substr(
               CASE 
                   WHEN json_extract(p.data, '$.type') = 'tool' 
                   THEN json_extract(p.data, '$.state.output')
                   ELSE NULL
               END, 1, 300
           ) as tool_output_preview
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE m.session_id = ?
    ORDER BY m.time_created, p.time_created
""", (SESSION_ID,))
for r in c.fetchall():
    row = dict(r)
    if row['part_type'] == 'text' and row['text']:
        role = row['role']
        text = row['text'][:300]
        print(f"[{role}] {text}")
    elif row['part_type'] == 'tool' and row['tool']:
        print(f"  TOOL: {row['tool']} -> {str(row.get('tool_output_preview', ''))[:150]}")

conn.close()
