import sqlite3
import json
import time

conn = sqlite3.connect(r'C:\Users\kalishd\.local\share\mimocode\mimocode.db')
cursor = conn.cursor()

# Get messages for the 3 real sessions (exclude the 4 auto-generated ones)
session_ids = [
    'ses_0de40df4effephtIr84xUCQODA',
    'ses_0de40e04fffedgl76LW5QTloUv', 
    'ses_0de40dfd2ffe3QDPh4A2p10Dea'
]

for sid in session_ids:
    cursor.execute("SELECT id, time_created, data FROM message WHERE session_id = ? ORDER BY time_created", (sid,))
    messages = cursor.fetchall()
    print(f"\n=== Session: {sid} ({len(messages)} messages) ===")
    
    for msg_id, created, data_json in messages:
        data = json.loads(data_json) if data_json else {}
        role = data.get('role', 'unknown')
        
        # Get parts for this message
        cursor.execute("SELECT data FROM part WHERE message_id = ?", (msg_id,))
        parts = cursor.fetchall()
        
        text_preview = ""
        tool_summary = []
        for (part_data_json,) in parts:
            part_data = json.loads(part_data_json) if part_data_json else {}
            if part_data.get('type') == 'text':
                text = part_data.get('text', '')[:300]
                text_preview += text + " "
            elif part_data.get('type') == 'tool':
                tool = part_data.get('tool', '?')
                inp = str(part_data.get('state', {}).get('input', ''))[:150]
                tool_summary.append(f"{tool}: {inp}")
        
        print(f"  [{role}] {text_preview[:200]}")
        if tool_summary:
            for t in tool_summary[:5]:
                print(f"    tool: {t}")

conn.close()
