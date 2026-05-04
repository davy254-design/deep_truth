from datetime import datetime
from extensions import db

class PDFReport(db.Model):
    __tablename__ = 'pdf_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_files.id'), nullable=False)
    report_number = db.Column(db.String(30), unique=True, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_report_number():
        count = PDFReport.query.count() + 1
        year = datetime.utcnow().year
        return f'RPT-{year}-{count:04d}'
    
    def __repr__(self):
        return f'<PDFReport {self.report_number}>'