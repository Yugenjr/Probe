import sqlite3
conn=sqlite3.connect(r'C:\Users\Yugendra\Downloads\Probe\packages\driftguard-sdk\driftguard_metadata.db')
conn.execute("UPDATE dg_users SET api_key_hash='1f8e8c97805e4ad56c611029fbba4c04dab40bf05d18c46655696357705cc136' WHERE id=1")
conn.commit()
