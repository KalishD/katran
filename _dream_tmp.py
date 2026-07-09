import sqlite3, json
from datetime import datetime, timedelta

DB_PATH = r'C:\Users\kalishd\.local\share\mimocode\mimocode.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get unique project_ids
cur.execute("SELECT DISTINCT project_id FROM session")
print("All project_ids:", [r[0] for r in cur.fetchall()])

# List all sessions with project_id and title, newest first
cur.execute("SELECT id, project_id, title, time_created, directory FROM session ORDER BY time_created DESC")
sessions = cur.fetchall()
print(f"\nTotal sessions: {len(sessions)}")
for s in sessions[:30]:
    ts = datetime.fromtimestamp(s[3]/1000).strftime('%Y-%m-%d %H:%M') if s[3] else 'None'
    print(f"  {s[0][:42]:<44} | {str(s[1])[:30]:<32} | {str(s[2])[:60]:<62} | {ts} | dir={str(s[4])[:50]}")

conn.close()
