from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import EvidenceFile
from models.analysis import AnalysisResult
from models.chain_of_custody import ChainOfCustody
from models.pdf_report import PDFReport
from services.forensic_service import ForensicService
from services.ai_service import AIService
from services.report_service import ReportService
from datetime import datetime
import os
import traceback

analysis_bp = Blueprint('analysis', __name__)

ALLOWED_VIDEO = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO | ALLOWED_IMAGE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return 'image' if ext in ALLOWED_IMAGE else 'video'

@analysis_bp.route('/single', methods=['GET', 'POST'])
@login_required
def single_analysis():
    # RBAC: Examiners see their cases, admins see all
    if current_user.role == 'admin':
        cases = Case.query.filter(Case.status != 'closed').order_by(Case.created_at.desc()).all()
    else:
        cases = Case.query.filter_by(investigator_id=current_user.id)\
            .filter(Case.status != 'closed').order_by(Case.created_at.desc()).all()
    
    if request.method == 'POST':
        if 'media_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['media_file']
        case_id = request.form.get('case_id')
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if not file or not allowed_file(file.filename):
            flash('Invalid file type. Allowed: MP4, AVI, MOV, JPG, PNG, etc.', 'danger')
            return redirect(request.url)
        
        if not case_id:
            flash('Please select a case.', 'danger')
            return redirect(request.url)
        
        case = Case.query.get_or_404(case_id)
        
        # RBAC check
        if current_user.role != 'admin' and case.investigator_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(request.url)
        
        try:
            media_type = get_media_type(file.filename)
            
            # Save uploaded file
            file_path, stored_filename = ForensicService.save_uploaded_file(
                file, current_app.config['UPLOAD_FOLDER']
            )
            
            file_size = os.path.getsize(file_path)
            sha256_hash = ForensicService.calculate_sha256(file_path)
            
            # Basic metadata
            metadata = {
                'file_name': file.filename,
                'file_size': file_size,
                'media_type': media_type,
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
            
            # Create evidence record
            evidence = EvidenceFile(
                case_id=case.id,
                evidence_number=f"EVD-{case.case_number}-{datetime.utcnow().strftime('%H%M%S%f')}",
                original_filename=file.filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type or 'application/octet-stream',
                media_type=media_type,
                sha256_hash=sha256_hash or 'pending',
                hash_timestamp=datetime.utcnow(),
                metadata_json=metadata,
                status='analyzing',
                uploaded_by=current_user.id
            )
            
            # Get resolution for images
            if media_type == 'image':
                try:
                    from PIL import Image
                    with Image.open(file_path) as img:
                        evidence.resolution_width = img.width
                        evidence.resolution_height = img.height
                except:
                    pass
            
            db.session.add(evidence)
            db.session.flush()
            
            # Chain of custody - submission
            coc1 = ChainOfCustody(
                evidence_id=evidence.id,
                action='submitted',
                description=f'{media_type.title()} file "{file.filename}" submitted to case {case.case_number}',
                performed_by=current_user.id,
                ip_address=request.remote_addr,
                timestamp=datetime.utcnow()
            )
            db.session.add(coc1)
            
            # Run AI analysis
            print(f"Running AI analysis on {media_type}: {file_path}")
            analysis_data = AIService.analyze_file(file_path, file.filename)
            print(f"Analysis complete: {analysis_data['classification']} - Score: {analysis_data['authenticity_score']}%")
            
            # Create analysis result
            analysis_result = AnalysisResult(
                evidence_id=evidence.id,
                analysis_type='single',
                authenticity_score=analysis_data['authenticity_score'],
                classification=analysis_data['classification'],
                manipulation_type=analysis_data.get('manipulation_type'),
                confidence=analysis_data['confidence'],
                feature_scores=analysis_data.get('feature_scores'),
                flagged_frames=analysis_data.get('flagged_frames', []),
                result_json=analysis_data,
                model_name=analysis_data['model_name'],
                model_version=analysis_data['model_version'],
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.session.add(analysis_result)
            
            # Chain of custody - analysis
            coc2 = ChainOfCustody(
                evidence_id=evidence.id,
                action='analyzed',
                description=f'AI analysis completed. Classification: {analysis_data["classification"].upper()}',
                performed_by=current_user.id,
                ip_address=request.remote_addr,
                timestamp=datetime.utcnow()
            )
            db.session.add(coc2)
            
            evidence.status = 'analyzed'
            
            # Generate PDF report
            try:
                report_number = PDFReport.generate_report_number()
                report_filename = f"{report_number}.pdf"
                report_dir = current_app.config['REPORT_FOLDER']
                os.makedirs(report_dir, exist_ok=True)
                report_path = os.path.join(report_dir, report_filename)
                
                ReportService.generate_single_analysis_report(
                    report_path, evidence, analysis_result, current_user.full_name
                )
                
                pdf_report = PDFReport(
                    evidence_id=evidence.id,
                    report_number=report_number,
                    file_path=report_path,
                    generated_by=current_user.id,
                    generated_at=datetime.utcnow()
                )
                db.session.add(pdf_report)
                
                # Chain of custody - report
                coc3 = ChainOfCustody(
                    evidence_id=evidence.id,
                    action='reported',
                    description=f'Forensic report {report_number} generated',
                    performed_by=current_user.id,
                    ip_address=request.remote_addr,
                    timestamp=datetime.utcnow()
                )
                db.session.add(coc3)
            except Exception as e:
                print(f"Report generation error: {e}")
                traceback.print_exc()
            
            db.session.commit()
            
            flash(f'Analysis complete! Classification: {analysis_data["classification"].upper()}', 'success')
            return redirect(url_for('analysis.view_result', evidence_id=evidence.id))
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('analysis/single.html', cases=cases)


@analysis_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def comparative_analysis():
    if current_user.role == 'admin':
        cases = Case.query.filter(Case.status != 'closed').order_by(Case.created_at.desc()).all()
    else:
        cases = Case.query.filter_by(investigator_id=current_user.id)\
            .filter(Case.status != 'closed').order_by(Case.created_at.desc()).all()
    
    if request.method == 'POST':
        print(f"Files in request: {request.files}")
        print(f"Form data: {request.form}")
        
        if 'media_a' not in request.files:
            flash('Please upload Media A.', 'danger')
            return redirect(request.url)
        if 'media_b' not in request.files:
            flash('Please upload Media B.', 'danger')
            return redirect(request.url)
        
        file_a = request.files['media_a']
        file_b = request.files['media_b']
        case_id = request.form.get('case_id')
        
        print(f"File A: {file_a.filename}, File B: {file_b.filename}")
        
        if file_a.filename == '':
            flash('Please select Media A.', 'danger')
            return redirect(request.url)
        if file_b.filename == '':
            flash('Please select Media B.', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file_a.filename):
            flash(f'Invalid file type for Media A.', 'danger')
            return redirect(request.url)
        if not allowed_file(file_b.filename):
            flash(f'Invalid file type for Media B.', 'danger')
            return redirect(request.url)
        
        if not case_id:
            flash('Please select a case.', 'danger')
            return redirect(request.url)
        
        case = Case.query.get_or_404(case_id)
        
        if current_user.role != 'admin' and case.investigator_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(request.url)
        
        try:
            timestamp = datetime.utcnow().strftime('%H%M%S%f')
            
            # Save both files
            file_path_a, stored_a = ForensicService.save_uploaded_file(
                file_a, current_app.config['UPLOAD_FOLDER']
            )
            file_path_b, stored_b = ForensicService.save_uploaded_file(
                file_b, current_app.config['UPLOAD_FOLDER']
            )
            
            print(f"Saved A: {file_path_a}, B: {file_path_b}")
            
            sha_a = ForensicService.calculate_sha256(file_path_a)
            sha_b = ForensicService.calculate_sha256(file_path_b)
            
            media_type_a = get_media_type(file_a.filename)
            media_type_b = get_media_type(file_b.filename)
            
            # Generate unique evidence numbers using timestamp
            ev_num_a = f"EVD-{case.case_number}-{timestamp}-A"
            ev_num_b = f"EVD-{case.case_number}-{timestamp}-B"
            
            # Evidence A
            evidence_a = EvidenceFile(
                case_id=case.id,
                evidence_number=ev_num_a,
                original_filename=file_a.filename,
                stored_filename=stored_a,
                file_path=file_path_a,
                file_size=os.path.getsize(file_path_a),
                mime_type=file_a.content_type or 'application/octet-stream',
                media_type=media_type_a,
                sha256_hash=sha_a or 'pending',
                status='analyzed',
                uploaded_by=current_user.id
            )
            db.session.add(evidence_a)
            db.session.flush()
            
            # Evidence B
            evidence_b = EvidenceFile(
                case_id=case.id,
                evidence_number=ev_num_b,
                original_filename=file_b.filename,
                stored_filename=stored_b,
                file_path=file_path_b,
                file_size=os.path.getsize(file_path_b),
                mime_type=file_b.content_type or 'application/octet-stream',
                media_type=media_type_b,
                sha256_hash=sha_b or 'pending',
                status='analyzed',
                uploaded_by=current_user.id
            )
            db.session.add(evidence_b)
            db.session.flush()
            
            # Run comparison
            comparison = AIService.compare_videos(
                file_path_a, file_path_b, file_a.filename, file_b.filename
            )
            
            # Save analysis results for both
            for ev, res_key in [(evidence_a, 'video_a'), (evidence_b, 'video_b')]:
                res = comparison[res_key]
                ar = AnalysisResult(
                    evidence_id=ev.id,
                    analysis_type='comparative',
                    reference_evidence_id=evidence_b.id if ev == evidence_a else evidence_a.id,
                    authenticity_score=res['authenticity_score'],
                    classification=res['classification'],
                    manipulation_type=res.get('manipulation_type'),
                    confidence=res['confidence'],
                    feature_scores=res.get('feature_scores'),
                    comparison_data=comparison,
                    result_json=res,
                    model_name=comparison['model_name'],
                    model_version=comparison['model_version'],
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow()
                )
                db.session.add(ar)
            
            # Chain of custody
            for ev in [evidence_a, evidence_b]:
                coc = ChainOfCustody(
                    evidence_id=ev.id,
                    action='submitted',
                    description=f'File submitted for comparative analysis',
                    performed_by=current_user.id,
                    ip_address=request.remote_addr,
                    timestamp=datetime.utcnow()
                )
                db.session.add(coc)
            
            # Generate PDF report for the comparison
            try:
                report_number = PDFReport.generate_report_number()
                report_filename = f"{report_number}.pdf"
                report_dir = current_app.config['REPORT_FOLDER']
                os.makedirs(report_dir, exist_ok=True)
                report_path = os.path.join(report_dir, report_filename)
                
                # Get the manipulated evidence's analysis
                manipulated_ev = evidence_b if comparison['manipulated_video'] == 'B' else evidence_a
                
                combined_analysis = AnalysisResult.query.filter_by(
                    evidence_id=manipulated_ev.id, analysis_type='comparative'
                ).first()
                
                if combined_analysis:
                    ReportService.generate_single_analysis_report(
                        report_path, manipulated_ev, combined_analysis, current_user.full_name
                    )
                    
                    pdf_report = PDFReport(
                        evidence_id=manipulated_ev.id,
                        report_number=report_number,
                        file_path=report_path,
                        generated_by=current_user.id,
                        generated_at=datetime.utcnow()
                    )
                    db.session.add(pdf_report)
                    
                    coc_report = ChainOfCustody(
                        evidence_id=manipulated_ev.id,
                        action='reported',
                        description=f'Comparative forensic report {report_number} generated',
                        performed_by=current_user.id,
                        ip_address=request.remote_addr,
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(coc_report)
            except Exception as e:
                print(f"PDF generation error: {e}")
                traceback.print_exc()
            
            db.session.commit()
            
            flash(f'Comparison complete! Media {comparison["authentic_video"]} appears authentic.', 'success')
            return render_template('analysis/compare_results.html', 
                                 result=comparison,
                                 evidence_a=evidence_a,
                                 evidence_b=evidence_b,
                                 cases=cases)
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('analysis/compare.html', cases=cases)


@analysis_bp.route('/result/<int:evidence_id>')
@login_required
def view_result(evidence_id):
    evidence = EvidenceFile.query.get_or_404(evidence_id)
    
    # RBAC check through the case
    if current_user.role != 'admin' and evidence.case.investigator_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    analysis_result = AnalysisResult.query.filter_by(evidence_id=evidence.id).first()
    pdf_reports = PDFReport.query.filter_by(evidence_id=evidence.id).order_by(PDFReport.generated_at.desc()).all()
    custody_entries = ChainOfCustody.query.filter_by(evidence_id=evidence.id).order_by(ChainOfCustody.timestamp.desc()).all()
    
    return render_template('analysis/result.html',
                         evidence=evidence,
                         analysis_result=analysis_result,
                         pdf_reports=pdf_reports,
                         custody_entries=custody_entries)


@analysis_bp.route('/download-report/<int:report_id>')
@login_required
def download_report(report_id):
    report = PDFReport.query.get_or_404(report_id)
    
    # RBAC check
    evidence = EvidenceFile.query.get(report.evidence_id)
    if evidence and current_user.role != 'admin' and evidence.case.investigator_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if report.file_path and os.path.exists(report.file_path):
        return send_file(
            report.file_path, 
            as_attachment=True, 
            download_name=f"{report.report_number}.pdf",
            mimetype='application/pdf'
        )
    else:
        flash('Report file not found.', 'danger')
        return redirect(url_for('dashboard.index'))