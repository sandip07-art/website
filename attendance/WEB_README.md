# Attendance Management System - Web Application

A modern, responsive web application for managing attendance using QR codes with three distinct portals: Admin, Teacher, and Student.

## 🌟 Features

### 🔐 Three-Portal System
- **Admin Portal**: Complete system administration, user management, and analytics
- **Teacher Portal**: Session creation, QR code generation, and attendance monitoring
- **Student Portal**: QR code scanning for attendance and personal attendance history

### 📱 Modern Web Interface
- Responsive design that works on all devices
- Bootstrap 5 with custom styling
- Real-time updates and notifications
- Interactive QR code scanner
- Mobile-friendly interface

### 🔒 Security Features
- User authentication and authorization
- Session management
- Secure QR code tokens
- Role-based access control

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Webcam (for QR code scanning)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r web_requirements.txt
   ```

2. **Run the Application**
   ```bash
   python web_app.py
   ```

3. **Access the Application**
   - Open your browser and go to `http://localhost:5000`
   - Default admin login: `admin` / `admin123`

## 📋 User Guide

### Admin Portal
- **Dashboard**: View system statistics and recent activity
- **User Management**: Add, edit, and manage users (teachers and students)
- **Reports**: Generate attendance reports and export data

### Teacher Portal
- **Create Sessions**: Set up attendance sessions with custom duration
- **QR Code Generation**: Generate QR codes for students to scan
- **Monitor Attendance**: View real-time attendance records
- **Session Management**: Track and manage multiple sessions

### Student Portal
- **QR Scanner**: Use webcam to scan teacher QR codes
- **Mark Attendance**: Instantly mark attendance by scanning
- **View History**: Check personal attendance records
- **Personal QR**: Access your own QR code for identification

## 🔧 Configuration

### Database
The application uses SQLite by default. To use a different database:

1. Update `app.config['SQLALCHEMY_DATABASE_URI']` in `web_app.py`
2. Install the appropriate database driver

### Security
- Change the default admin password immediately
- Update `app.config['SECRET_KEY']` for production
- Use HTTPS in production environments

## 📁 Project Structure

```
attendance/
├── web_app.py              # Main Flask application
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Landing page
│   ├── login.html         # Login page
│   ├── admin/             # Admin portal templates
│   ├── teacher/           # Teacher portal templates
│   └── student/           # Student portal templates
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── main.js        # JavaScript functionality
├── web_requirements.txt   # Python dependencies
└── WEB_README.md         # This file
```

## 🎯 Key Features Explained

### QR Code System
- **Teacher QR Codes**: Contain session tokens for attendance marking
- **Student QR Codes**: Personal identification codes
- **Secure Tokens**: Time-limited, encrypted session tokens

### Real-time Updates
- Live attendance tracking
- Instant notifications
- Automatic session expiration

### Mobile Responsiveness
- Works on smartphones, tablets, and desktops
- Touch-friendly interface
- Optimized for mobile QR scanning

## 🔧 API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout

### Admin
- `GET /admin` - Admin dashboard
- `GET /admin/users` - User management
- `POST /admin/add_user` - Create new user

### Teacher
- `GET /teacher` - Teacher dashboard
- `POST /teacher/create_session` - Create session
- `GET /teacher/session/<id>` - Session details

### Student
- `GET /student` - Student dashboard
- `POST /student/scan_qr` - Scan QR code

## 🚀 Deployment

### Local Development
```bash
python web_app.py
```

### Production Deployment
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up a reverse proxy (Nginx)
3. Use a production database (PostgreSQL, MySQL)
4. Enable HTTPS
5. Set up proper logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY web_requirements.txt .
RUN pip install -r web_requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "web_app.py"]
```

## 🛠️ Customization

### Styling
- Modify `static/css/style.css` for custom styling
- Update Bootstrap theme variables
- Add custom animations and effects

### Functionality
- Extend `web_app.py` with additional routes
- Add new database models
- Implement additional features

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: User email
- `password_hash`: Hashed password
- `user_type`: admin/teacher/student
- `name`: Full name
- `created_at`: Creation timestamp

### Sessions Table
- `id`: Primary key
- `teacher_id`: Foreign key to users
- `session_name`: Session name
- `qr_token`: Unique QR token
- `is_active`: Session status
- `created_at`: Creation timestamp
- `expires_at`: Expiration timestamp

### Attendance Table
- `id`: Primary key
- `student_id`: Foreign key to users
- `teacher_id`: Foreign key to users
- `session_name`: Session name
- `timestamp`: Attendance timestamp
- `qr_data`: QR code data

## 🔒 Security Considerations

- Always use HTTPS in production
- Implement rate limiting for login attempts
- Regular security updates
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Flask auto-escaping)

## 📞 Support

For issues and questions:
1. Check the console logs for errors
2. Verify camera permissions for QR scanning
3. Ensure all dependencies are installed
4. Check database connectivity

## 🎉 Success!

Your attendance management system is now ready! The web application provides a modern, user-friendly interface for managing attendance with QR codes across three distinct user portals.
