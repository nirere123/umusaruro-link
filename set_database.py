import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Benjamin@32',
    database='umusaruro_link'
)
cursor = conn.cursor()

print("Checking and creating database tables if they don't exist...")

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'equip_owner') NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✓ Users table ready")

# Create farmers table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    farm_location VARCHAR(255),
    crop_type VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("✓ Farmers table ready")

# Create equipment table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    location VARCHAR(100),
    photo VARCHAR(255),
    image_filename VARCHAR(255) DEFAULT NULL,
    availability ENUM('available', 'unavailable') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("✓ Equipment table ready")

# Create rentals table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    equipment_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') DEFAULT 'pending',
    message TEXT,
    total_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
)
""")
print("✓ Rentals table ready")

# Create trust_history table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS trust_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT UNIQUE NOT NULL,
    completed_rentals INT DEFAULT 0,
    cancelled_rentals INT DEFAULT 0,
    score DECIMAL(3, 2) DEFAULT 0.00,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("✓ Trust history table ready")

# Create notifications table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("✓ Notifications table ready")

# Create messages table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("✓ Messages table ready")

# Create payments table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    farmer_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('paid', 'failed', 'pending') DEFAULT 'pending',
    payment_date DATE,
    payment_method VARCHAR(50) DEFAULT 'MTN Mobile Money',
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rentals(id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("✓ Payments table ready")

conn.commit()
print("\n✓ All tables are ready!")
print("\nYou can now:")
print("1. Refresh your browser")
print("2. Register a new account (if not already registered)")
print("3. Login and start using the app")

cursor.close()
conn.close()
