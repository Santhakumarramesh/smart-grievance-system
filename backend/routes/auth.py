from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import hashlib
from backend.models import User, OTPRequest
from backend.extensions import db
from backend.config import Config
from backend.services.otp_service import OTPService
from backend.services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)

def create_token(user_id):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    Required: name, email, phone, password
    Optional: aadhaar_last4, consent
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            role='CITIZEN'
        )
        user.set_password(data['password'])
        
        # Handle Aadhaar (optional)
        if data.get('aadhaar_last4'):
            user.aadhaar_last4 = data['aadhaar_last4']
            # Hash full aadhaar if provided (for demo, we only store last 4)
            user.aadhaar_hash = hashlib.sha256(data['aadhaar_last4'].encode()).hexdigest()
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful. Please verify your email.',
            'user_id': user.id,
            'email': user.email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """
    Send OTP to email or phone
    Required: identifier (email or phone), channel ('email' or 'phone')
    """
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        channel = data.get('channel', 'email')
        
        if not identifier:
            return jsonify({'error': 'identifier is required'}), 400
        
        if channel not in ['email', 'phone']:
            return jsonify({'error': 'channel must be email or phone'}), 400
        
        # Generate and send OTP
        otp, error = OTPService.create_otp_request(identifier, channel)
        
        if error:
            return jsonify({'error': error}), 429
        
        return jsonify({
            'message': f'OTP sent to {identifier} via {channel}',
            'demo_mode': Config.DEMO_EMAIL_MODE or Config.DEMO_SMS_MODE,
            'demo_note': 'Check console for OTP in demo mode'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP and mark user as verified
    Required: identifier, otp
    """
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        otp = data.get('otp')
        
        if not identifier or not otp:
            return jsonify({'error': 'identifier and otp are required'}), 400
        
        # Verify OTP
        success, message = OTPService.verify_otp(identifier, otp)
        
        if not success:
            return jsonify({'error': message}), 400
        
        # Find user and mark as verified
        user = User.query.filter_by(email=identifier).first()
        if not user:
            user = User.query.filter_by(phone=identifier).first()
        
        if user:
            if '@' in identifier:
                user.email_verified = True
            else:
                user.phone_verified = True
            db.session.commit()
            
            # Send welcome email
            EmailService.send_welcome_email(user.email, user.name)
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    Required: email, password
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create token
        token = create_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current user info from token
    Requires: Authorization header with Bearer token
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_current_user_from_token():
    """
    Helper function to get current user from request token
    Returns: User object or None
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        
        if not user_id:
            return None
        
        return User.query.get(user_id)
        
    except:
        return None
