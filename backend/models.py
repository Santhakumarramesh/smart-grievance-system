from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='CITIZEN')  # CITIZEN, OFFICER, ADMIN
    department = db.Column(db.String(100), nullable=True)  # For officers
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    aadhaar_last4 = db.Column(db.String(4), nullable=True)
    aadhaar_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    grievances = db.relationship('Grievance', backref='user', lazy=True, foreign_keys='Grievance.user_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'department': self.department,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class OTPRequest(db.Model):
    __tablename__ = 'otp_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(120), nullable=False, index=True)  # email or phone
    otp_hash = db.Column(db.String(255), nullable=False)
    channel = db.Column(db.String(10), nullable=False)  # 'email' or 'phone'
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_otp(self, otp):
        self.otp_hash = generate_password_hash(str(otp))
    
    def check_otp(self, otp):
        return check_password_hash(self.otp_hash, str(otp))


class Grievance(db.Model):
    __tablename__ = 'grievances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    predicted_department = db.Column(db.String(100), nullable=False)
    assigned_department = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Received')
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updates = db.relationship('GrievanceUpdate', backref='grievance', lazy=True, order_by='GrievanceUpdate.timestamp')
    comments = db.relationship('GrievanceComment', backref='grievance', lazy=True, order_by='GrievanceComment.created_at')
    
    def to_dict(self, include_updates=False, include_comments=False):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'complaint_text': self.complaint_text,
            'predicted_department': self.predicted_department,
            'assigned_department': self.assigned_department,
            'status': self.status,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_updates:
            result['updates'] = [update.to_dict() for update in self.updates]
        if include_comments:
            result['comments'] = [comment.to_dict() for comment in self.comments]
        return result


class GrievanceUpdate(db.Model):
    __tablename__ = 'grievance_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey('grievances.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    updated_by_role = db.Column(db.String(20), nullable=False)  # SYSTEM, OFFICER, ADMIN
    updated_by_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notify_sent = db.Column(db.Boolean, default=False)
    notify_sent_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'grievance_id': self.grievance_id,
            'status': self.status,
            'message': self.message,
            'updated_by_role': self.updated_by_role,
            'updated_by_name': self.updated_by_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notify_sent': self.notify_sent,
        }


class GrievanceComment(db.Model):
    __tablename__ = 'grievance_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey('grievances.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    user_role = db.Column(db.String(20), nullable=False)  # CITIZEN, OFFICER, ADMIN
    user_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comments', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'grievance_id': self.grievance_id,
            'user_id': self.user_id,
            'comment_text': self.comment_text,
            'user_role': self.user_role,
            'user_name': self.user_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
