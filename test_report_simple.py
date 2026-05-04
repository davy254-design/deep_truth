"""Simple test to check if ReportLab works on your system"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import os

# Test path
test_path = os.path.join(os.path.dirname(__file__), 'reports', 'output', 'TEST_SIMPLE.pdf')
os.makedirs(os.path.dirname(test_path), exist_ok=True)

print(f"Creating test PDF at: {test_path}")

try:
    doc = SimpleDocTemplate(test_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph("TEST REPORT", styles['Heading1']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("This is a test to verify ReportLab works correctly.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("If you can read this, PDF generation is working!", styles['Normal']))
    
    doc.build(story)
    
    if os.path.exists(test_path):
        print(f"SUCCESS! PDF created at: {test_path}")
        print(f"File size: {os.path.getsize(test_path)} bytes")
    else:
        print("FAILED: PDF file was not created")
        
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    print("ReportLab may not be installed correctly.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()