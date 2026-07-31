import sqlite3
conn=sqlite3.connect(r'C:\Users\Yugendra\Downloads\Probe\packages\driftguard-sdk\driftguard_metadata.db')
conn.execute("UPDATE dg_users SET api_key_hash='d0e574dbaa999f459f487c94d191ecb7ebe5e74c58865cb4aad15dfe0fab43d4' WHERE id=1")
conn.commit()
