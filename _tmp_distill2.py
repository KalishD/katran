import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\kalishd\.local\share\mimocode\mimocode.db')
cursor = conn.cursor()

# Get tool usage frequency across all sessions
cutoff_ms = 1780385846561  # 30 days ago
cursor.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           substr(json_extract(p.data, '$.state.input'), 1, 200) as input_preview,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND m.time_created > ?
    GROUP BY tool, input_preview
    ORDER BY n DESC
    LIMIT 50
""", (cutoff_ms,))
rows = cursor.fetchall()
print("=== Tool usage frequency (last 30 days) ===")
for tool, inp, n in rows:
    print(f"  {n}x  {tool}: {inp[:120]}")

# Also check for repeated keywords in user messages
print("\n=== User message keywords ===")
cursor.execute("""
    SELECT json_extract(m.data, '$.role') as role, substr(json_extract(p.data, '$.text'), 1, 300) as text
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'user'
      AND m.time_created > ?
""", (cutoff_ms,))
rows = cursor.fetchall()
for role, text in rows:
    if text:
        # Check for repeat keywords
        lower = text.lower()
        markers = []
        for kw in ['снова', 'опять', 'как в прошлый', 'как обычно', 'повтори', 'так же', 'по аналогии', 'again', 'same as', 'repeat', 'like before', 'the usual']:
            if kw in lower:
                markers.append(kw)
        if markers:
            print(f"  REPEAT KEYWORDS {markers}: {text[:150]}")

# Check tasks
print("\n=== Tasks ===")
cursor.execute("SELECT id, session_id, status, summary FROM task")
for row in cursor.fetchall():
    print(f"  task {row[0]}: session={row[1]}, status={row[2]}, summary={row[3]}")

conn.close()
