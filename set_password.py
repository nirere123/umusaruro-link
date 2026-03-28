import mysql.connector

# Connect to XAMPP MySQL (no password initially)
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='mysql'
)
cursor = conn.cursor()

# Set password
cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY 'Benjamin@32'")
conn.commit()

print('✓ Password changed to Benjamin@32')
cursor.close()
conn.close()
