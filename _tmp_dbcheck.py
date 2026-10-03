import sqlite3

conn = sqlite3.connect(r'C:\Users\kalishd\.local\share\mimocode\mimocode.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

# Get session count and date range
for t in ['session', 'message', 'part']:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
        cnt = cursor.fetchone()[0]
        print(f"  {t}: {cnt} rows")
    except Exception as e:
        print(f"  {t}: error - {e}")

# Date range
try:
    cursor.execute("SELECT MIN(time_created), MAX(time_created) FROM session")
    row = cursor.fetchone()
    print(f"Session time range: {row[0]} - {row[1]}")
except Exception as e:
    print(f"Session range error: {e}")

# Recent sessions (last 30 days = ~30*86400*1000 ms)
import time
cutoff_ms = int((time.time() - 30*86400) * 1000)
print(f"\nCutoff (30 days ago) ms: {cutoff_ms}")

try:
    cursor.execute("SELECT id, time_created, title FROM session ORDER BY time_created DESC LIMIT 20")
    rows = cursor.fetchall()
    for r in rows:
        sid, created, title = r
        marker = " <-- within 30d" if created and created > cutoff_ms else ""
        print(f"  session {sid}: time={created}, title={title}{marker}")
except Exception as e:
    print(f"Recent sessions error: {e}")

conn.close()
