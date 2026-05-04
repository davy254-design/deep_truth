from app import create_app
from extensions import db
from models.user import User, AuditLog
from models.case import Case
from models.evidence import EvidenceFile
from models.analysis import AnalysisResult
from models.chain_of_custody import ChainOfCustody
from models.pdf_report import PDFReport
from datetime import datetime

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Create admin user
    if not User.query.filter_by(email='admin@deeptruth.com').first():
        admin = User(
            email='admin@deeptruth.com',
            username='admin',
            full_name='System Administrator',
            badge_number='DF-ADMIN',
            role='admin',  # THIS IS THE ADMIN
            is_active=True
        )
        admin.set_password('Admin@2026')
        db.session.add(admin)
        print("Admin user created!")
    
    # Create examiner users
    if not User.query.filter_by(email='edwin@deeptruth.com').first():
        examiner1 = User(
            email='edwin@deeptruth.com',
            username='edwin',
            full_name='Edwin Ochieng',
            badge_number='DF-002',
            role='examiner',
            is_active=True
        )
        examiner1.set_password('Examiner@2026')
        db.session.add(examiner1)
        print("Examiner Edwin created!")
    
    if not User.query.filter_by(email='david@deeptruth.com').first():
        examiner2 = User(
            email='david@deeptruth.com',
            username='david',
            full_name='David Ouma Ochieng',
            badge_number='DF-003',
            role='examiner',
            is_active=True
        )
        examiner2.set_password('Examiner@2026')
        db.session.add(examiner2)
        print("Examiner David created!")
    
    db.session.commit()
    
    print("\n" + "="*50)
    print("Seed completed successfully!")
    print("="*50)
    print("\nTest Credentials:")
    print("  ADMIN:  admin@deeptruth.com / Admin@2026")
    print("  Edwin:  edwin@deeptruth.com / Examiner@2026")
    print("  David:  david@deeptruth.com / Examiner@2026")
    print("\nNOTE: Admin can see ALL cases and user activity.")
    print("      Examiners can only see their own cases.")