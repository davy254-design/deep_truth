from flask import Blueprint, render_template, send_file
from flask_login import login_required
from extensions import db
from models.pdf_report import PDFReport

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def list_reports():
    reports = PDFReport.query.order_by(PDFReport.generated_at.desc()).all()
    return render_template('reports/list.html', reports=reports)

@reports_bp.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    report = PDFReport.query.get_or_404(report_id)
    return send_file(
        report.file_path,
        as_attachment=True,
        download_name=f"{report.report_number}.pdf",
        mimetype='application/pdf'
    )