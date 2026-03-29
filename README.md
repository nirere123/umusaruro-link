# Umusaruro Link

## Equipment Rental & Farmer Connection Platform for Rwanda

Umusaruro Link is a comprehensive web platform that connects farmers in Rwanda with equipment owners, enabling easy rental of agricultural machinery and fostering community connections among farmers.

### Features

#### For Farmers
- **Browse Equipment**: Search and filter available equipment by location, price, and type
- **Rent Equipment**: Request rentals with approval workflow
- **Farmer Directory**: Connect with other farmers in your area
- **Knowledge Feed**: Access agricultural tips and best practices
- **Trust System**: Build reputation through completed rentals
- **Messaging**: Communicate with equipment owners and other farmers

#### For Equipment Owners
- **List Equipment**: Add, edit, and manage your equipment listings
- **Manage Rentals**: Approve/reject rental requests and track equipment usage
- **Payment Tracking**: Monitor rental payments and earnings
- **Availability Calendar**: View equipment booking schedules

#### For Administrators
- **User Management**: View and manage all platform users
- **System Monitoring**: Access to user statistics and platform metrics

### Tech Stack

- **Backend**: Python 3.11+, Flask 3.1.0
- **Database**: MySQL 8.0+
- **Frontend**: Bootstrap 5.3, Jinja2 templates
- **Authentication**: bcrypt password hashing
- **File Storage**: Local file system for equipment images

### Installation & Setup

#### Prerequisites
- Python 3.11 or higher
- MySQL 8.0 or higher
- Git

#### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd umusaruro-link
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up database**
   - Create a MySQL database named `umusaruro_link`
   - Run the SQL script to create tables:
     ```sql
     mysql -u root -p umusaruro_link < database.sql
     ```

6. **Configure database connection**
   - Update `config.py` with your MySQL credentials if different from defaults

7. **Run the application**
   ```bash
   python APIs/app.py
   ```

8. **Access the application**
   - Open http://localhost:5000 in your browser
   - Register as a new user or login

### Project Structure

```
umusaruro-link/
├── APIs/
│   └── app.py                 # Main Flask application
├── authentication/
│   └── auth.py                # Authentication routes
├── database/
│   ├── db.py                  # Database connection utilities
│   └── database.sql           # Database schema
├── equipment/
│   └── equipment.py           # Equipment management
├── farmers/
│   ├── farmers.py             # Farmer features
│   └── __init__.py
├── messages/
│   └── messages.py            # Messaging system
├── payments/
│   └── payments.py            # Payment handling
├── rental/
│   └── rental.py              # Rental management
├── admin/
│   └── admin.py               # Admin panel
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── static/                    # Static assets
│   ├── css/
│   ├── img/
│   └── uploads/               # Equipment images
└── templates/                 # Jinja2 templates
    ├── base.html              # Base layout
    ├── macros.html            # Template macros
    ├── auth/                  # Authentication templates
    ├── equipment/             # Equipment templates
    ├── farmers/               # Farmer templates
    ├── messages/              # Message templates
    ├── payments/              # Payment templates
    ├── profile/               # User profile templates
    ├── notifications/         # Notification templates
    ├── admin/                 # Admin templates
    └── errors/                # Error page templates
```

### Database Schema

The application uses MySQL with the following main tables:

- `users` - User accounts (farmers, equipment owners, admins)
- `equipment` - Equipment listings
- `rentals` - Rental requests and transactions
- `farmers` - Additional farmer-specific information
- `trust_history` - Farmer reputation scores
- `notifications` - User notifications
- `messages` - Private messaging between users
- `payments` - Payment records

### API Endpoints

#### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `POST /logout` - User logout

#### Equipment
- `GET /equipment` - Browse equipment (with search/filters)
- `GET/POST /add-equipment` - Add new equipment
- `GET/POST /edit-equipment/<id>` - Edit equipment
- `POST /delete-equipment/<id>` - Delete equipment

#### Rentals
- `POST /rent/<equipment_id>` - Request equipment rental
- `GET /manage-rentals` - View rental requests (owners)
- `POST /approve-rental/<id>` - Approve rental request
- `POST /reject-rental/<id>` - Reject rental request

#### Profile
- `GET /profile/` - View user profile
- `GET/POST /profile/edit` - Edit profile
- `GET/POST /profile/change-password` - Change password

#### Farmers
- `GET /farmers` - Farmer directory
- `GET /farmers/knowledge` - Knowledge feed
- `POST /connect/<farmer_id>` - Send connection request

#### Messages
- `GET /messages` - Inbox
- `GET /conversation/<user_id>` - Chat with user
- `POST /send-message` - Send message

#### Notifications
- `GET /notifications` - View notifications
- `GET /notifications/count` - Get unread count (JSON)

#### Admin
- `GET /admin` - Admin dashboard
- `GET /admin/users` - User management

### Security Features

- **Password Hashing**: bcrypt for secure password storage
- **SQL Injection Protection**: Parameterized queries throughout
- **Session Management**: Flask session handling
- **File Upload Validation**: Extension and size limits
- **Role-based Access**: Different permissions for user types

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Support

For support or questions, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for Rwandan farmers**
