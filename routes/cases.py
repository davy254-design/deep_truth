from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import EvidenceFile
from models.user import User
from datetime import datetime

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/')
@login_required
def list_cases():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    # RBAC: Admins see all, examiners see only their cases
    if current_user.role == 'admin':
        query = Case.query
        base_count_query = Case.query
    else:
        query = Case.query.filter_by(investigator_id=current_user.id)
        base_count_query = Case.query.filter_by(investigator_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(
            db.or_(
                Case.case_number.ilike(f'%{search_query}%'),
                Case.title.ilike(f'%{search_query}%'),
                Case.description.ilike(f'%{search_query}%')
            )
        )
    
    query = query.order_by(Case.created_at.desc())
    cases = query.paginate(page=page, per_page=10, error_out=False)
    
    total_open = base_count_query.filter_by(status='open').count()
    total_in_progress = base_count_query.filter_by(status='in_progress').count()
    total_closed = base_count_query.filter_by(status='closed').count()
    
    return render_template('cases/list.html', 
                         cases=cases, 
                         status_filter=status_filter,
                         search_query=search_query,
                         total_open=total_open,
                         total_in_progress=total_in_progress,
                         total_closed=total_closed)

@cases_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_case():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        case_type = request.form.get('case_type')
        priority = request.form.get('priority', 'medium')
        
        # Admin can assign to any examiner
        if current_user.role == 'admin':
            assigned_to = request.form.get('assigned_to')
            investigator_id = int(assigned_to) if assigned_to else current_user.id
        else:
            investigator_id = current_user.id
        
        if not title:
            flash('Case title is required.', 'danger')
            users = User.query.filter_by(role='examiner', is_active=True).all()
            return render_template('cases/create.html', users=users)
        
        case = Case(
            case_number=Case.generate_case_number(),
            title=title,
            description=description,
            case_type=case_type,
            priority=priority,
            investigator_id=investigator_id
        )
        
        db.session.add(case)
        db.session.commit()
        
        flash(f'Case {case.case_number} created successfully!', 'success')
        return redirect(url_for('cases.view_case', case_id=case.id))
    
    users = User.query.filter_by(role='examiner', is_active=True).all()
    return render_template('cases/create.html', users=users)

@cases_bp.route('/<int:case_id>')
@login_required
def view_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # RBAC check
    if current_user.role != 'admin' and case.investigator_id != current_user.id:
        flash('Access denied. This is not your case.', 'danger')
        return redirect(url_for('cases.list_cases'))
    
    evidence_files = case.evidence_files.order_by(EvidenceFile.upload_timestamp.desc()).all()
    return render_template('cases/view.html', case=case, evidence_files=evidence_files)

@cases_bp.route('/<int:case_id>/update-status', methods=['POST'])
@login_required
def update_case_status(case_id):
    case = Case.query.get_or_404(case_id)
    
    if current_user.role != 'admin' and case.investigator_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cases.list_cases'))
    
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if new_status in ['open', 'in_progress', 'closed']:
        case.status = new_status
        if new_status == 'closed':
            case.closed_at = datetime.utcnow()
        if notes:
            case.notes = notes
        db.session.commit()
        flash(f'Case {case.case_number} status updated to {new_status}.', 'success')
    
    return redirect(url_for('cases.view_case', case_id=case_id))