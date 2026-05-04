from app import create_app
from extensions import db
from models.evidence import EvidenceFile
from models.analysis import AnalysisResult
from models.pdf_report import PDFReport
from models.chain_of_custody import ChainOfCustody
from services.report_service import ReportService
from datetime import datetime
import os
import traceback

app = create_app()

with app.app_context():
    # Get existing evidence
    evidence = EvidenceFile.query.first()
    analysis = AnalysisResult.query.first()
    
    if evidence and analysis:
        print(f"Evidence found: ID={evidence.id}, Number={evidence.evidence_number}")
        print(f"Analysis found: ID={analysis.id}, Classification={analysis.classification}")
        
        report_dir = app.config['REPORT_FOLDER']
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, 'TEST_DEBUG_REPORT.pdf')
        
        try:
            print(f"\nGenerating test report at: {report_path}")
            print(f"Evidence object type: {type(evidence)}")
            print(f"Analysis object type: {type(analysis)}")
            
            ReportService.generate_single_analysis_report(
                report_path, evidence, analysis, "Test Examiner"
            )
            
            if os.path.exists(report_path):
                print(f"\n✅ SUCCESS! Report generated!")
                print(f"File: {report_path}")
                print(f"Size: {os.path.getsize(report_path)} bytes")
            else:
                print(f"\n❌ FAILED: File not created at {report_path}")
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print(f"Error type: {type(e).__name__}")
            print("\nFull traceback:")
            traceback.print_exc()
    else:
        print("No evidence or analysis found in database.")
        if not evidence:
            print("  - No evidence files exist")
        if not analysis:
            print("  - No analysis results exist")