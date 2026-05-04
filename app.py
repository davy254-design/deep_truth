from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager, migrate
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader for Flask-Login
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.cases import cases_bp
    from routes.analysis import analysis_bp
    from routes.reports import reports_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(cases_bp, url_prefix='/cases')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp)
    
    # Create upload and report directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
    
    # Create database tables
    with app.app_context():
        # Import all models to ensure they're registered
        from models.user import User
        from models.case import Case
        from models.evidence import EvidenceFile
        from models.analysis import AnalysisResult
        from models.chain_of_custody import ChainOfCustody
        from models.pdf_report import PDFReport
        
        db.create_all()
    
    # Root route redirects to login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)