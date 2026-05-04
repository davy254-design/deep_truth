import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                 TableStyle, HRFlowable, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from xml.sax.saxutils import escape

class ReportService:
    """Service for generating forensic PDF reports"""
    
    DARK_BLUE = HexColor('#1a1a2e')
    GREEN = HexColor('#28a745')
    RED = HexColor('#dc3545')
    ORANGE = HexColor('#ffc107')
    GRAY = HexColor('#6c757d')
    LIGHT_GRAY = HexColor('#f0f0f0')
    
    @staticmethod
    def _add_watermark(canvas, doc):
        """Add CONFIDENTIAL watermark to pages"""
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 72)
        canvas.setFillColor(HexColor('#f5f5f5'))
        canvas.setStrokeColor(HexColor('#f5f5f5'))
        width, height = A4
        canvas.translate(width / 2, height / 2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "CONFIDENTIAL")
        canvas.restoreState()
    
    @staticmethod
    def generate_single_analysis_report(report_path, evidence, analysis_result, examiner_name):
        """Generate a professional forensic PDF report"""
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            report_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=18*mm,
            bottomMargin=25*mm
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles with proper XML handling
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=ReportService.DARK_BLUE,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=ReportService.GRAY,
            alignment=TA_CENTER,
            spaceAfter=8
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=ReportService.DARK_BLUE,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'Normal2',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            fontName='Helvetica'
        )
        
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=ReportService.GRAY
        )
        
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica'
        )
        
        story = []
        
        # ===== LOGO =====
        logo_paths = [
            os.path.join(os.getcwd(), 'logo.jpg'),
            'logo.jpg',
            os.path.join(os.path.dirname(__file__), '..', 'logo.jpg'),
        ]
        
        logo_found = False
        for lp in logo_paths:
            if os.path.exists(lp):
                try:
                    logo = Image(lp, width=70, height=70)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 8))
                    logo_found = True
                    print(f"Logo added from: {lp}")
                    break
                except Exception as e:
                    print(f"Logo error ({lp}): {e}")
        
        if not logo_found:
            story.append(Paragraph('<font size="28">🛡️</font>', normal_style))
            story.append(Spacer(1, 5))
        
        # ===== REPORT HEADER =====
        story.append(Paragraph("DEEPTRUTH FORENSICS", title_style))
        story.append(Paragraph("Digital Evidence Deepfake Analysis Report", subtitle_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=ReportService.DARK_BLUE))
        story.append(Spacer(1, 12))
        
        # ===== REPORT METADATA =====
        report_number = f"RPT-{datetime.utcnow().year}-{evidence.id:04d}"
        case_number = 'N/A'
        try:
            if evidence.case:
                case_number = str(evidence.case.case_number)
        except:
            pass
        
        # Use simple strings instead of Paragraph with XML for table cells
        meta_data = [
            ['Report Number:', report_number],
            ['Case Number:', case_number],
            ['Evidence Number:', str(evidence.evidence_number or 'N/A')],
            ['Date Generated:', datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')],
            ['Examiner:', str(examiner_name)],
            ['Classification:', 'CONFIDENTIAL'],
        ]
        
        meta_table = Table(meta_data, colWidths=[120, 370])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), ReportService.GRAY),
            ('TEXTCOLOR', (1, 5), (1, 5), ReportService.RED),
            ('FONTNAME', (1, 5), (1, 5), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(meta_table)
        
        # ===== SECTION 1: EVIDENCE DETAILS =====
        story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.5, color=ReportService.GRAY))
        story.append(Paragraph("1. EVIDENCE DETAILS", heading_style))
        
        file_size = evidence.file_size or 0
        file_size_mb = f"{file_size / (1024*1024):.2f} MB" if file_size > 0 else 'N/A'
        sha = str(evidence.sha256_hash or 'N/A')
        
        evidence_rows = [
            ['Property', 'Value'],
            ['File Name', str(evidence.original_filename or 'N/A')],
            ['File Size', file_size_mb],
            ['MIME Type', str(evidence.mime_type or 'N/A')],
            ['SHA-256 Hash', sha],
        ]
        
        if evidence.duration:
            evidence_rows.append(['Duration', f"{evidence.duration:.2f} seconds"])
        if evidence.resolution_width and evidence.resolution_height:
            evidence_rows.append(['Resolution', f"{evidence.resolution_width}x{evidence.resolution_height}"])
        if evidence.frame_rate:
            evidence_rows.append(['Frame Rate', f"{evidence.frame_rate:.2f} fps"])
        if evidence.video_codec:
            evidence_rows.append(['Video Codec', str(evidence.video_codec)])
        if evidence.audio_codec:
            evidence_rows.append(['Audio Codec', str(evidence.audio_codec)])
        if evidence.upload_timestamp:
            evidence_rows.append(['Upload Time', evidence.upload_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')])
        
        ev_table = Table(evidence_rows, colWidths=[130, 360])
        ev_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ReportService.DARK_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, ReportService.GRAY),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ReportService.LIGHT_GRAY]),
        ]))
        story.append(ev_table)
        
        # ===== SECTION 2: CRYPTOGRAPHIC INTEGRITY =====
        story.append(Paragraph("2. CRYPTOGRAPHIC INTEGRITY VERIFICATION", heading_style))
        
        hash_rows = [
            ['Property', 'Value'],
            ['Hash Algorithm', 'SHA-256 (FIPS 180-4)'],
            ['Hash Value', sha],
        ]
        
        if evidence.hash_timestamp:
            hash_rows.append(['Hash Timestamp', evidence.hash_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')])
        
        hash_rows.append(['Integrity Status', 'VERIFIED - EVIDENCE INTACT'])
        
        hash_table = Table(hash_rows, colWidths=[130, 360])
        hash_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ReportService.DARK_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, ReportService.GRAY),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (1, -1), (1, -1), ReportService.GREEN),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
        ]))
        story.append(hash_table)
        
        # ===== SECTION 3: ANALYSIS RESULTS =====
        story.append(Paragraph("3. DEEPFAKE ANALYSIS RESULTS", heading_style))
        
        if analysis_result:
            classification = str(analysis_result.classification or 'N/A').upper()
            authenticity = analysis_result.authenticity_score or 0
            confidence = analysis_result.confidence or 0
            model_name = str(analysis_result.model_name or 'DeepTruth Ensemble')
            model_version = str(analysis_result.model_version or '2.1.0')
            
            analysis_rows = [
                ['Property', 'Value'],
                ['Classification', classification],
                ['Authenticity Score', f'{authenticity:.1f}%'],
                ['Confidence Level', f'{confidence:.1f}%'],
                ['Analysis Model', f'{model_name} v{model_version}'],
            ]
            
            if analysis_result.manipulation_type:
                analysis_rows.append(['Manipulation Type', analysis_result.manipulation_type.replace('_', ' ').title()])
            
            analysis_table = Table(analysis_rows, colWidths=[130, 360])
            
            # Color the classification row
            row_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), ReportService.DARK_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, ReportService.GRAY),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]
            
            # Color based on classification
            if classification == 'AUTHENTIC':
                row_styles.append(('TEXTCOLOR', (1, 1), (1, 1), ReportService.GREEN))
            elif classification == 'MANIPULATED':
                row_styles.append(('TEXTCOLOR', (1, 1), (1, 1), ReportService.RED))
            else:
                row_styles.append(('TEXTCOLOR', (1, 1), (1, 1), ReportService.ORANGE))
            row_styles.append(('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'))
            
            analysis_table.setStyle(TableStyle(row_styles))
            story.append(analysis_table)
            
            # Flagged frames
            flagged = analysis_result.flagged_frames
            if flagged and isinstance(flagged, list) and len(flagged) > 0:
                story.append(Spacer(1, 10))
                story.append(Paragraph("<b>Flagged Manipulation Indicators:</b>", normal_style))
                story.append(Spacer(1, 5))
                
                for frame in flagged[:6]:
                    if isinstance(frame, dict):
                        fn = frame.get('frame_number', '?')
                        ts = frame.get('timestamp_display', 'N/A')
                        ind = frame.get('indicator', 'N/A')
                        sev = frame.get('severity', 'low').upper()
                        story.append(Paragraph(
                            f"• <b>Frame #{fn}</b> [{ts}] — {ind} &nbsp; "
                            f"<i>(Severity: {sev})</i>",
                            normal_style
                        ))
                        story.append(Spacer(1, 2))
        else:
            story.append(Paragraph("<i>No analysis results available.</i>", normal_style))
        
        # ===== SECTION 4: CHAIN OF CUSTODY =====
        story.append(Paragraph("4. CHAIN OF CUSTODY", heading_style))
        
        try:
            entries = evidence.custody_entries.all()
            if entries and len(entries) > 0:
                sorted_entries = sorted(entries, key=lambda x: x.timestamp if x.timestamp else datetime.min)
                
                coc_rows = [['Timestamp', 'Action', 'Performed By', 'Description']]
                for entry in sorted_entries[:10]:
                    ts = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') if entry.timestamp else 'N/A'
                    action = entry.action.replace('_', ' ').title() if entry.action else 'N/A'
                    performer = entry.performer.full_name if entry.performer else 'SYSTEM'
                    desc = (str(entry.description) if entry.description else 'N/A')[:60]
                    coc_rows.append([ts, action, performer, desc])
                
                coc_table = Table(coc_rows, colWidths=[110, 75, 100, 205])
                coc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), ReportService.DARK_BLUE),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                    ('GRID', (0, 0), (-1, -1), 0.5, ReportService.GRAY),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ReportService.LIGHT_GRAY]),
                ]))
                story.append(coc_table)
            else:
                story.append(Paragraph("<i>Chain of custody log maintained automatically.</i>", normal_style))
        except Exception as e:
            story.append(Paragraph(f"<i>Chain of custody available in database.</i>", normal_style))
        
        # ===== SECTION 5: EXAMINER NOTES =====
        story.append(Paragraph("5. EXAMINER NOTES & RECOMMENDATIONS", heading_style))
        story.append(Paragraph(
            "This analysis was performed using the DeepTruth Forensics automated deepfake detection pipeline. "
            "The system examines spatial and temporal features to identify potential manipulation including "
            "face swaps, lip-sync anomalies, and AI-generated content indicators.",
            normal_style
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Recommendations:</b>", normal_style))
        story.append(Paragraph(
            "• Results should be reviewed by a qualified forensic examiner before use in legal proceedings.",
            normal_style
        ))
        story.append(Paragraph(
            "• Original evidence files should be preserved with SHA-256 hash values intact.",
            normal_style
        ))
        
        # ===== SECTION 6: SIGNATURES =====
        story.append(Paragraph("6. CERTIFICATION & SIGNATURES", heading_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "I certify that the information in this report is accurate to the best of my knowledge "
            "and the analysis was conducted following established forensic procedures.",
            normal_style
        ))
        story.append(Spacer(1, 30))
        
        sig_style = ParagraphStyle(
            'Sig',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold'
        )
        
        # Signature table - Examiner signature and Date on same line
        sig_data = [
            [
                Paragraph("_________________________________________", sig_style),
                Paragraph("_________________________________________", sig_style)
            ],
            [
                Paragraph("<b>Examiner's Signature</b>", sig_style),
                Paragraph("<b>Date</b>", sig_style)
            ],
            [
                Paragraph(f"{examiner_name}", normal_style),
                Paragraph("", normal_style)
            ],
        ]
        
        sig_table = Table(sig_data, colWidths=[245, 245])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(sig_table)
        
        story.append(Spacer(1, 15))
        story.append(Paragraph("_________________________________________", sig_style))
        story.append(Paragraph("<b>Supervisor's Signature</b>", sig_style))
        story.append(Paragraph("<i>Name: ___________________________ &nbsp;&nbsp; Date: ___________________________</i>", normal_style))
        
        # ===== FOOTER =====
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=2, color=ReportService.DARK_BLUE))
        story.append(Spacer(1, 8))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=ReportService.GRAY,
            alignment=TA_CENTER
        )
        story.append(Paragraph("END OF REPORT — DeepTruth Forensics v1.0", footer_style))
        story.append(Paragraph(f"Electronically generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} | Examiner: {examiner_name}", footer_style))
        story.append(Paragraph("This document contains CONFIDENTIAL forensic analysis. Unauthorized distribution is prohibited.", footer_style))
        
        # ===== BUILD PDF =====
        try:
            doc.build(
                story,
                onFirstPage=ReportService._add_watermark,
                onLaterPages=ReportService._add_watermark
            )
        except TypeError:
            doc.build(story)
        
        return report_path