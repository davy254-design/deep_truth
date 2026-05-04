from datetime import datetime
from extensions import db

class EvidenceFile(db.Model):
    __tablename__ = 'evidence_files'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    evidence_number = db.Column(db.String(30), unique=True, nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger)
    mime_type = db.Column(db.String(50))
    media_type = db.Column(db.String(10), default='video')  # 'video' or 'image'
    duration = db.Column(db.Float)
    resolution_width = db.Column(db.Integer)
    resolution_height = db.Column(db.Integer)
    frame_rate = db.Column(db.Float)
    video_codec = db.Column(db.String(50))
    audio_codec = db.Column(db.String(50))
    
    sha256_hash = db.Column(db.String(64), nullable=False)
    md5_hash = db.Column(db.String(32))
    hash_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metadata_json = db.Column(db.JSON)
    status = db.Column(db.String(20), default='pending')
    upload_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    custody_entries = db.relationship('ChainOfCustody', backref='evidence', lazy='dynamic')
    pdf_reports = db.relationship('PDFReport', backref='evidence', lazy='dynamic')
    
    @staticmethod
    def generate_evidence_number(case_number):
        from app import create_app
        app = create_app()
        with app.app_context():
            count = EvidenceFile.query.count() + 1
        return f'EVD-{case_number}-{count:03d}'
    
    def __repr__(self):
        return f'<EvidenceFile {self.evidence_number}>'