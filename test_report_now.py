from app import create_app
from extensions import db
from models.evidence import EvidenceFile
from models.analysis import AnalysisResult
from models.pdf_report import PDFReport
from models.chain_of_custody import ChainOfCustody
from datetime import datetime
import os
import traceback

app = create_app()

with app.app_context():
    evidence = EvidenceFile.query.first()
    analysis = AnalysisResult.query.first()
    
    if evidence and analysis:
        print(f"Evidence: {evidence.evidence_number}")
        print(f"Analysis: {analysis.classification} - Score: {analysis.authenticity_score}%")
        
        # Try to generate report directly here
        try:
            from services.report_service import ReportService
            
            report_dir = app.config['REPORT_FOLDER']
            os.makedirs(report_dir, exist_ok=True)
            
            report_path = os.path.join(report_dir, 'TEST_NOW.pdf')
            print(f"\nGenerating report at: {report_path}")
            
            # Test each step individually
            print("1. Checking evidence attributes...")
            print(f"   - evidence_number: {evidence.evidence_number}")
            print(f"   - original_filename: {evidence.original_filename}")
            print(f"   - file_size: {evidence.file_size}")
            print(f"   - sha256_hash: {evidence.sha256_hash[:20] if evidence.sha256_hash else 'None'}...")
            
            print("2. Checking analysis attributes...")
            print(f"   - classification: {analysis.classification}")
            print(f"   - authenticity_score: {analysis.authenticity_score}")
            print(f"   - confidence: {analysis.confidence}")
            print(f"   - flagged_frames: {type(analysis.flagged_frames)}")
            if analysis.flagged_frames:
                print(f"   - flagged_frames count: {len(analysis.flagged_frames)}")
            
            print("3. Trying to access custody entries...")
            try:
                custody = evidence.custody_entries.all()
                print(f"   - Custody entries: {len(custody)}")
            except Exception as e:
                print(f"   - Custody error: {e}")
            
            print("4. Calling ReportService...")
            ReportService.generate_single_analysis_report(
                report_path, evidence, analysis, "Test Examiner"
            )
            
            if os.path.exists(report_path):
                print(f"\n✅ SUCCESS! Report: {report_path} ({os.path.getsize(report_path)} bytes)")
            else:
                print(f"\n❌ File not created")
                
        except Exception as e:
            print(f"\n❌ ERROR: {type(e).__name__}: {e}")
            print("\nFull traceback:")
            traceback.print_exc()
    else:
        print("No data found. Please run an analysis first.")
        print(f"Evidence: {evidence}")
        print(f"Analysis: {analysis}")