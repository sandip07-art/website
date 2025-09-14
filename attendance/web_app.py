#!/usr/bin/env python3
"""
Web Application for Attendance Monitoring System
Three Portals: Admin, Teacher, Student
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import cv2
import base64
import io
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import qrcode
from qrcode.constants import ERROR_CORRECT_H

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_name = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    qr_data = db.Column(db.Text, nullable=True)
    
    student = db.relationship('User', foreign_keys=[student_id], backref='attendance_records')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='taught_sessions')

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_name = db.Column(db.String(200), nullable=False)
    qr_token = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    teacher = db.relationship('User', backref='sessions')

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@attendance.com',
            user_type='admin',
            name='System Administrator'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Utility Functions
def generate_qr_code(data):
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

def decode_qr_from_image(image_data):
    """Decode QR code from base64 image data"""
    try:
        # Remove data URL prefix
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Decode QR code
        decoded_objects = decode(opencv_image)
        
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        print(f"QR decode error: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        user = User.query.filter_by(username=username, user_type=user_type).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            session['name'] = user.name
            
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_type == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user_type == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Admin Portal
@app.route('/admin')
def admin_dashboard():
    if not session.get('user_id') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    # Get statistics
    total_users = User.query.count()
    total_teachers = User.query.filter_by(user_type='teacher').count()
    total_students = User.query.filter_by(user_type='student').count()
    total_attendance = Attendance.query.count()
    
    recent_attendance = db.session.query(Attendance, User).join(
        User, Attendance.student_id == User.id
    ).order_by(Attendance.timestamp.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_teachers=total_teachers,
                         total_students=total_students,
                         total_attendance=total_attendance,
                         recent_attendance=recent_attendance)

@app.route('/admin/users')
def admin_users():
    if not session.get('user_id') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
def admin_add_user():
    if not session.get('user_id') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        name = request.form['name']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('admin/add_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('admin/add_user.html')
        
        user = User(
            username=username,
            email=email,
            user_type=user_type,
            name=name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html')

# Teacher Portal
@app.route('/teacher')
def teacher_dashboard():
    if not session.get('user_id') or session.get('user_type') != 'teacher':
        return redirect(url_for('login'))
    
    teacher_id = session['user_id']
    
    # Get teacher's sessions
    sessions = Session.query.filter_by(teacher_id=teacher_id).order_by(Session.created_at.desc()).all()
    
    # Get attendance statistics
    total_attendance = Attendance.query.filter_by(teacher_id=teacher_id).count()
    today_attendance = Attendance.query.filter(
        Attendance.teacher_id == teacher_id,
        Attendance.timestamp >= datetime.now().date()
    ).count()
    
    return render_template('teacher/dashboard.html',
                         sessions=sessions,
                         total_attendance=total_attendance,
                         today_attendance=today_attendance)

@app.route('/teacher/create_session', methods=['GET', 'POST'])
def teacher_create_session():
    if not session.get('user_id') or session.get('user_type') != 'teacher':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        session_name = request.form['session_name']
        duration_hours = int(request.form['duration_hours'])
        
        # Generate unique token
        import secrets
        token = secrets.token_hex(16)
        
        # Create session
        new_session = Session(
            teacher_id=session['user_id'],
            session_name=session_name,
            qr_token=token,
            expires_at=datetime.utcnow() + timedelta(hours=duration_hours)
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        flash('Session created successfully', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/create_session.html')

@app.route('/teacher/session/<int:session_id>')
def teacher_session_details(session_id):
    if not session.get('user_id') or session.get('user_type') != 'teacher':
        return redirect(url_for('login'))
    
    session_obj = Session.query.get_or_404(session_id)
    
    # Get attendance for this session
    attendance_records = db.session.query(Attendance, User).join(
        User, Attendance.student_id == User.id
    ).filter(Attendance.session_name == session_obj.session_name).all()
    
    # Generate QR code for session
    qr_data = f"TEACHER_TOKEN:{session_obj.qr_token}"
    qr_code = generate_qr_code(qr_data)
    
    return render_template('teacher/session_details.html',
                         session=session_obj,
                         attendance_records=attendance_records,
                         qr_code=qr_code)

# Student Portal
@app.route('/student')
def student_dashboard():
    if not session.get('user_id') or session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    student_id = session['user_id']
    
    # Get student's attendance records
    attendance_records = db.session.query(Attendance, User).join(
        User, Attendance.teacher_id == User.id
    ).filter(Attendance.student_id == student_id).order_by(Attendance.timestamp.desc()).all()
    
    # Generate student QR code
    student_data = f"STUDENT:{session['username']}:{session['name']}"
    student_qr = generate_qr_code(student_data)
    
    return render_template('student/dashboard.html',
                         attendance_records=attendance_records,
                         student_qr=student_qr)

@app.route('/student/scan_qr', methods=['POST'])
def student_scan_qr():
    if not session.get('user_id') or session.get('user_type') != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    image_data = request.json.get('image_data')
    if not image_data:
        return jsonify({'success': False, 'message': 'No image data provided'})
    
    # Decode QR code
    qr_data = decode_qr_from_image(image_data)
    if not qr_data:
        return jsonify({'success': False, 'message': 'No QR code found in image'})
    
    # Check if it's a teacher token
    if qr_data.startswith('TEACHER_TOKEN:'):
        token = qr_data.split(':', 1)[1]
        
        # Find active session with this token
        session_obj = Session.query.filter_by(qr_token=token, is_active=True).first()
        
        if not session_obj:
            return jsonify({'success': False, 'message': 'Invalid or expired session token'})
        
        if session_obj.expires_at < datetime.utcnow():
            return jsonify({'success': False, 'message': 'Session has expired'})
        
        # Check if already marked attendance for this session
        existing_attendance = Attendance.query.filter_by(
            student_id=session['user_id'],
            session_name=session_obj.session_name
        ).first()
        
        if existing_attendance:
            return jsonify({'success': False, 'message': 'Already marked attendance for this session'})
        
        # Mark attendance
        attendance = Attendance(
            student_id=session['user_id'],
            teacher_id=session_obj.teacher_id,
            session_name=session_obj.session_name,
            qr_data=qr_data
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked for {session_obj.session_name}',
            'session_name': session_obj.session_name
        })
    
    return jsonify({'success': False, 'message': 'Invalid QR code format'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
