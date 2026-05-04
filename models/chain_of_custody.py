from datetime import datetime
from extensions import db

class ChainOfCustody(db.Model):
    __tablename__ = 'chain_of_custody'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_files.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    
    def __repr__(self):
        return f'<ChainOfCustody {self.action} at {self.timestamp}>'