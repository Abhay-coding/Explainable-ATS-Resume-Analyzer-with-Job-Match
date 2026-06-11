import io
import logging
import re
import html as html_lib
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors

logger = logging.getLogger('ats_resume_scorer')

def clean_html_for_pdf(html_str: str) -> str:
    """
    Aggressively clean HTML to extract only text content, removing all style/script/tag markup
    """
    # Remove script tags and content
    html_str = re.sub(r'<script[^>]*>.*?</script>', '', html_str, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags and content - this is the critical part
    html_str = re.sub(r'<style[^>]*>.*?</style>', '', html_str, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    html_str = re.sub(r'<!--.*?-->', '', html_str, flags=re.DOTALL)
    
    # Remove all HTML tags but keep the content
    html_str = re.sub(r'<[^>]+>', '\n', html_str)
    
    # Decode HTML entities (e.g., &nbsp; → space)
    html_str = html_lib.unescape(html_str)
    
    # Clean up excessive whitespace
    lines = []
    for line in html_str.split('\n'):
        line = line.strip()
        # Remove CSS rules (lines starting with . or # or containing :)
        if line and not re.match(r'^[.#]', line) and ':' not in line[:20]:
            # Skip lines that look like CSS
            if '{' not in line and '}' not in line and 'font-' not in line and 'color:' not in line:
                lines.append(line)
    
    return '\n'.join(lines)

def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    """
    Generate PDF from HTML documents using ReportLab
    (Windows-compatible alternative to WeasyPrint which requires GTK)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        topMargin=0.5*inch, 
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for better readability
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=12,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        alignment=0,
        wordWrap='CJK'
    )
    
    # Add each section
    for idx, (section_name, html_str) in enumerate(html_docs.items()):
        # Add page break between sections (except before first)
        if idx > 0:
            story.append(PageBreak())
        
        # Add section title
        story.append(Paragraph(section_name, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Clean and extract text content
        text_content = clean_html_for_pdf(html_str)
        
        # Split into non-empty lines and add to PDF
        if text_content:
            lines = text_content.split('\n')
            for line in lines:
                line = line.strip()
                # Skip empty lines and CSS-looking lines
                if line and len(line) > 2 and not line.startswith('/*') and not line.startswith('*'):
                    try:
                        story.append(Paragraph(line, body_style))
                        story.append(Spacer(1, 0.05*inch))
                    except Exception as e:
                        logger.debug(f"Skipped problematic line: {line[:50]}")
                        continue
    
    # Add footer
    story.append(Spacer(1, 0.3*inch))
    footer = f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by ATS Resume Analyzer"
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    story.append(Paragraph(footer, footer_style))
    
    # Build PDF
    try:
        doc.build(story)
    except Exception as e:
        logger.error(f"Error building PDF: {e}")
        # Fallback: create simple text-only PDF
        raise
    
    return buffer.getvalue()