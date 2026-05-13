# Deep Truth

## AI-Based Deepfake Detection and Automated evidence preservation Platform

Deep Truth is a comprehensive web-based platform designed for forensic analysis and detection of deepfake media. Built with Flask and powered by advanced AI algorithms, it provides investigators with tools to analyze video and image files for deepfake indicators, manage cases, maintain chain of custody, and generate detailed reports.

## Features

### 🔍 Deepfake Detection
- **Multi-Feature Analysis**: Comprehensive analysis using noise patterns, compression artifacts, color consistency, edge analysis, frequency domain analysis, and metadata verification
- **Media Support**: Supports analysis of images (JPG, PNG, BMP, GIF, TIFF, WebP) and videos (MP4, AVI, MOV, MKV, WebM)
- **Ensemble Scoring**: Weighted scoring system combining multiple detection methods for high accuracy

### 📁 Case Management
- **Case Creation**: Create and manage forensic cases with unique case numbers
- **Evidence Handling**: Upload and organize evidence files with automatic hashing (SHA-256, MD5)
- **Chain of Custody**: Maintain complete audit trail of evidence handling
- **Status Tracking**: Track case progress from open to closed

### 👥 User Management
- **Role-Based Access**: Admin, Examiner, and Investigator roles with appropriate permissions
- **Authentication**: Secure login system with password hashing
- **Audit Logging**: Comprehensive logging of all user activities

### 📊 Analysis & Reporting
- **Real-time Analysis**: Instant deepfake detection results
- **Comparison Tools**: Compare multiple media files for authenticity
- **PDF Reports**: Generate detailed forensic reports with analysis results
- **Dashboard**: Overview of cases, analyses, and system status

### 🛡️ Security & Compliance
- **File Integrity**: SHA-256 and MD5 hashing for evidence verification
- **Secure Uploads**: Configurable file size limits and type restrictions
- **Session Management**: Secure session handling with configurable timeouts

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/davy254-design/deep_truth.git
   cd deep_truth
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   ```bash
   python seed.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

### Default Credentials
- **Admin**: admin@deeptruth.com / Admin@2026
- **Examiner**: edwin@deeptruth.com / Examiner@2026
- **Examiner**: david@deeptruth.com / Examiner@2026

## Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
USE_POSTGRES=true  # Set to true for PostgreSQL, false for SQLite
DATABASE_URL=postgresql://username:password@localhost:5432/deeptruth_forensics
```

### Database Options
- **SQLite** (default): No additional setup required, suitable for development
- **PostgreSQL**: For production use, set `USE_POSTGRES=true` and provide `DATABASE_URL`

### Upload Configuration
- Maximum file size: 500MB (configurable in `config.py`)
- Supported formats: MP4, AVI, MOV, MKV, WebM for videos; JPG, PNG, BMP, GIF, TIFF, WebP for images

## Usage

### Getting Started
1. Log in with your credentials
2. Create a new case from the dashboard
3. Upload evidence files
4. Run deepfake analysis
5. Generate and download reports

### API Endpoints
The application provides RESTful API endpoints for integration:

- `POST /auth/login` - User authentication
- `GET /cases` - List cases
- `POST /cases` - Create new case
- `POST /analysis/analyze` - Analyze media file
- `GET /reports/{id}` - Get analysis report

### File Analysis
Upload media files through the web interface or API. The system will:
1. Calculate file hashes for integrity verification
2. Extract metadata (duration, resolution, codec, etc.)
3. Run AI analysis for deepfake detection
4. Store results in the database
5. Generate downloadable reports

## Testing

Run the test suite:
```bash
python -m pytest test_*.py
```

Available test files:
- `test_report.py` - Report generation tests
- `test_report_simple.py` - Basic report tests
- `test_report_now.py` - Current report functionality tests

## Project Structure

```
deep_truth/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── extensions.py         # Flask extensions (DB, Login, Migrate)
├── seed.py               # Database seeding script
├── requirements.txt      # Python dependencies
├── models/               # Database models
│   ├── user.py          # User management
│   ├── case.py          # Case management
│   ├── evidence.py      # Evidence files
│   ├── analysis.py      # Analysis results
│   ├── chain_of_custody.py
│   └── pdf_report.py    # Report generation
├── routes/               # Flask blueprints
│   ├── auth.py          # Authentication
│   ├── dashboard.py     # Main dashboard
│   ├── cases.py         # Case management
│   ├── analysis.py      # Analysis interface
│   ├── reports.py       # Report generation
│   └── admin.py         # Admin panel
├── services/             # Business logic
│   ├── ai_service.py    # Deepfake detection
│   └── forensic_service.py # Forensic utilities
├── templates/            # Jinja2 templates
├── static/               # CSS, JS, uploads
└── reports/              # Generated reports
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `python -m pytest`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Write unit tests for new features
- Update documentation for API changes

## Security Considerations

- Change default passwords in production
- Use strong SECRET_KEY
- Enable HTTPS in production
- Regularly update dependencies
- Monitor upload file types and sizes
- Implement proper access controls

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- **David Ouma Ochieng** - *Developer/Forensics Specialist* - [davy254-design](https://github.com/davy254-design)
- **Edwin Ochieng** - *Developer/Forensics Specialist*

## Acknowledgments

- Built with Flask web framework
- AI analysis powered by OpenCV and NumPy
- PDF generation using ReportLab
- UI styled with Bootstrap

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation for common solutions

---

**Deep Truth** - Uncovering the truth in digital media through advanced forensic analysis.</content>
<filePath>README.md
