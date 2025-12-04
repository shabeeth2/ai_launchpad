import sqlite3

conn = sqlite3.connect('uk_health_insurance.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {tables}")

if tables:
    table_name = tables[0][0]
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    print(f"\nFirst 5 rows from {table_name}:")
    for row in rows:
        print(row)
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows: {count}")
else:
    print("No tables found in the database")

conn.close()
