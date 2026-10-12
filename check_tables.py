import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=finance_tracker;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

query = """
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
"""

try:
    with pyodbc.connect(connection_string, timeout=5) as connection:
        cursor = connection.cursor()
        cursor.execute(query)

        current_table = None
        for row in cursor.fetchall():
            if row.TABLE_NAME != current_table:
                current_table = row.TABLE_NAME
                print(f"\n--- dbo.{current_table} ---")
                print("Column | Type | Nullable | Default")

            print(
                f"{row.COLUMN_NAME} | {row.DATA_TYPE} | "
                f"{row.IS_NULLABLE} | {row.COLUMN_DEFAULT}"
            )

except pyodbc.Error as error:
    print("Database error:", error)
