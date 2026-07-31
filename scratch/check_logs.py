import sqlite3
conn=sqlite3.connect(r'C:\Users\Yugendra\Downloads\Probe\packages\driftguard-sdk\driftguard_metadata.db')
print(len(conn.execute("SELECT * FROM dg_audit_logs WHERE model_id='credit-risk-v1'").fetchall()))
print(conn.execute("SELECT event_type FROM dg_audit_logs WHERE model_id='credit-risk-v1'").fetchall())
