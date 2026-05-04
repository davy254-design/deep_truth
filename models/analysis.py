from datetime import datetime
from extensions import db

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_files.id'), nullable=False)
    analysis_type = db.Column(db.String(30), nullable=False)  # single, comparative
    reference_evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_files.id'), nullable=True)
    
    # Scores
    authenticity_score = db.Column(db.Float)
    classification = db.Column(db.String(30))
    manipulation_type = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    
    # Detailed feature analysis
    feature_scores = db.Column(db.JSON)  # Individual feature scores
    comparison_data = db.Column(db.JSON)  # For comparative analysis
    flagged_frames = db.Column(db.JSON)
    result_json = db.Column(db.JSON)
    
    model_name = db.Column(db.String(100))
    model_version = db.Column(db.String(20))
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    evidence = db.relationship('EvidenceFile', foreign_keys=[evidence_id], 
                               backref=db.backref('analysis_results', lazy='dynamic'))
    reference_evidence = db.relationship('EvidenceFile', foreign_keys=[reference_evidence_id],
                                         backref=db.backref('referenced_by_analyses', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AnalysisResult {self.id}>'