import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\kalishd\.local\share\mimocode\mimocode.db')
cursor = conn.cursor()

# Check the 3 older sessions (before 30 days) for patterns
cursor.execute("SELECT id, time_created, title FROM session ORDER BY time_created ASC LIMIT 3")
rows = cursor.fetchall()
print("=== Older sessions ===")
for sid, created, title in rows:
    print(f"\n--- Session: {sid} (time={created}, title={title}) ---")
    cursor.execute("SELECT id, time_created, data FROM message WHERE session_id = ? ORDER BY time_created", (sid,))
    messages = cursor.fetchall()
    for msg_id, created, data_json in messages:
        data = json.loads(data_json) if data_json else {}
        role = data.get('role', 'unknown')
        
        cursor.execute("SELECT data FROM part WHERE message_id = ?", (msg_id,))
        parts = cursor.fetchall()
        
        text_preview = ""
        tool_summary = []
        for (part_data_json,) in parts:
            part_data = json.loads(part_data_json) if part_data_json else {}
            if part_data.get('type') == 'text':
                text = part_data.get('text', '')[:400]
                text_preview += text + " "
            elif part_data.get('type') == 'tool':
                tool = part_data.get('tool', '?')
                inp = str(part_data.get('state', {}).get('input', ''))[:200]
                tool_summary.append(f"{tool}: {inp}")
        
        print(f"  [{role}] {text_preview[:250]}")
        if tool_summary:
            for t in tool_summary[:8]:
                print(f"    tool: {t}")

# Also check what auto-generated sessions are
print("\n\n=== Auto-generated sessions ===")
cursor.execute("SELECT id, time_created, title FROM session ORDER BY time_created DESC LIMIT 4")
rows = cursor.fetchall()
for sid, created, title in rows:
    print(f"\n--- Session: {sid} (title={title}) ---")
    cursor.execute("SELECT id, data FROM message WHERE session_id = ? ORDER BY time_created", (sid,))
    messages = cursor.fetchall()
    for msg_id, data_json in messages:
        data = json.loads(data_json) if data_json else {}
        role = data.get('role', 'unknown')
        cursor.execute("SELECT data FROM part WHERE message_id = ?", (msg_id,))
        parts = cursor.fetchall()
        for (part_data_json,) in parts:
            part_data = json.loads(part_data_json) if part_data_json else {}
            if part_data.get('type') == 'text':
                print(f"  [{role}] {part_data.get('text', '')[:200]}")
                break

conn.close()
