# FILE: config.py
# MEMBER: Configuration Team
# PURPOSE: Central configuration file for all app settings

import os

# Flask Configuration
SECRET_KEY = 'umusaruro-link-secret-2026'

# MySQL Database Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Benjamin@32'
MYSQL_DB = 'umusaruro_link'

# File Upload Configuration
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max upload
UPLOAD_FOLDER = 'assets/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
