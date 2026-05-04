from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    badge_number = db.Column(db.String(50), unique=True)
    role = db.Column(db.String(20), default='examiner')  # admin, examiner
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_logout = db.Column(db.DateTime)
    total_time_spent = db.Column(db.Integer, default=0)  # in seconds
    
    # Relationships
    cases = db.relationship('Case', backref='investigator', lazy='dynamic')
    evidence_uploads = db.relationship('EvidenceFile', backref='uploader', lazy='dynamic',
                                       foreign_keys='EvidenceFile.uploaded_by')
    custody_actions = db.relationship('ChainOfCustody', backref='performer', lazy='dynamic',
                                      foreign_keys='ChainOfCustody.performed_by')
    generated_reports = db.relationship('PDFReport', backref='generator', lazy='dynamic',
                                        foreign_keys='PDFReport.generated_by')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action} at {self.timestamp}>'