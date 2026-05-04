from datetime import datetime
from extensions import db

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    case_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='medium')
    investigator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationships
    evidence_files = db.relationship('EvidenceFile', backref='case', lazy='dynamic')
    
    @staticmethod
    def generate_case_number():
        last_case = Case.query.order_by(Case.id.desc()).first()
        if last_case:
            next_id = last_case.id + 1
        else:
            next_id = 1
        year = datetime.utcnow().year
        return f'CASE-{year}-{next_id:04d}'
    
    def __repr__(self):
        return f'<Case {self.case_number}>'