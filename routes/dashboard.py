from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.case import Case
from models.evidence import EvidenceFile
from models.analysis import AnalysisResult
from models.pdf_report import PDFReport
from models.user import User, AuditLog
from extensions import db
from sqlalchemy import and_

dashboard_bp = Blueprint('dashboard', __name__)

def format_time(seconds):
    """Format seconds to readable time string"""
    if not seconds:
        return "0s"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard - redirects based on role"""
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    
    # Examiner stats (only their cases)
    total_cases = Case.query.filter_by(investigator_id=current_user.id).count()
    open_cases = Case.query.filter_by(investigator_id=current_user.id, status='open').count()
    
    # Count evidence for user's cases - use explicit join
    total_evidence = EvidenceFile.query.join(
        Case, EvidenceFile.case_id == Case.id
    ).filter(
        Case.investigator_id == current_user.id
    ).count()
    
    analyzed_evidence = EvidenceFile.query.join(
        Case, EvidenceFile.case_id == Case.id
    ).filter(
        Case.investigator_id == current_user.id,
        EvidenceFile.status == 'analyzed'
    ).count()
    
    # Count deepfakes detected - use explicit join with foreign key
    deepfakes_detected = AnalysisResult.query.join(
        EvidenceFile, AnalysisResult.evidence_id == EvidenceFile.id
    ).join(
        Case, EvidenceFile.case_id == Case.id
    ).filter(
        Case.investigator_id == current_user.id,
        AnalysisResult.classification == 'manipulated'
    ).count()
    
    # Count reports - use explicit join
    total_reports = PDFReport.query.join(
        EvidenceFile, PDFReport.evidence_id == EvidenceFile.id
    ).join(
        Case, EvidenceFile.case_id == Case.id
    ).filter(
        Case.investigator_id == current_user.id
    ).count()
    
    stats = {
        'total_cases': total_cases,
        'open_cases': open_cases,
        'total_evidence': total_evidence,
        'analyzed_evidence': analyzed_evidence,
        'deepfakes_detected': deepfakes_detected,
        'total_reports': total_reports
    }
    
    recent_cases = Case.query.filter_by(investigator_id=current_user.id)\
        .order_by(Case.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, recent_cases=recent_cases)

@dashboard_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin Dashboard - sees everything"""
    if current_user.role != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # System-wide stats
    total_users = User.query.count()
    total_cases = Case.query.count()
    total_evidence = EvidenceFile.query.count()
    total_analyses = AnalysisResult.query.count()
    deepfakes_detected = AnalysisResult.query.filter_by(classification='manipulated').count()
    total_reports = PDFReport.query.count()
    
    stats = {
        'total_users': total_users,
        'total_cases': total_cases,
        'total_evidence': total_evidence,
        'total_analyses': total_analyses,
        'deepfakes_detected': deepfakes_detected,
        'total_reports': total_reports
    }
    
    # All users with their stats
    users = User.query.all()
    user_stats = []
    for user in users:
        user_cases = Case.query.filter_by(investigator_id=user.id).count()
        user_evidence = EvidenceFile.query.filter_by(uploaded_by=user.id).count()
        user_stats.append({
            'user': user,
            'cases_count': user_cases,
            'evidence_count': user_evidence,
            'time_spent': format_time(user.total_time_spent or 0)
        })
    
    # Recent audit logs
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(20).all()
    
    # Recent cases (all)
    recent_cases = Case.query.order_by(Case.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         user_stats=user_stats,
                         audit_logs=audit_logs,
                         recent_cases=recent_cases)