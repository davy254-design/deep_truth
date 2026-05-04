import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'deeptruth-secret-key-change-in-production'
    
    # Database - Use SQLite for development, PostgreSQL for production
    # Set USE_POSTGRES=true in environment to use PostgreSQL
    if os.environ.get('USE_POSTGRES') == 'true':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'postgresql://postgres:postgres@localhost:5432/deeptruth_forensics'
    else:
        # SQLite fallback - no installation needed
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'deeptruth.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max upload
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    
    # Report settings
    REPORT_FOLDER = os.path.join(basedir, 'reports', 'output')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Remember me
    REMEMBER_COOKIE_DURATION = timedelta(days=14)