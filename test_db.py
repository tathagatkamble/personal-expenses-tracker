from db import get_connection

try:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'dbo'
              AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)

        print("Flask database connection test: SUCCESS")
        print("Tables:")
        for row in cursor.fetchall():
            print("-", row[0])

except Exception as error:
    print("Connection test failed:", error)
