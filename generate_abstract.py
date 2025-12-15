from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_abstract():
    doc = SimpleDocTemplate(
        "SmartJob_Aggregator_Abstract.pdf",
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=4 # Justify
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=20
    )

    story = []

    # Title
    story.append(Paragraph("SmartJob Aggregator", title_style))
    story.append(Paragraph("Intelligent Job Search & Resume Automation Platform", 
        ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=30)))

    # Abstract
    story.append(Paragraph("Abstract", heading_style))
    abstract_text = """
    In the current competitive job market, candidates often struggle with a fragmented landscape where opportunities are scattered across multiple platforms (LinkedIn, Indeed, Glassdoor, etc.). Additionally, tailoring resumes to pass Application Tracking Systems (ATS) is a time-consuming and often misunderstood process. 
    <br/><br/>
    <b>SmartJob Aggregator</b> addresses these challenges by providing a unified platform that aggregates job listings from various sources into a single, searchable interface. Beyond simple aggregation, the platform features an intelligent "Smart Profile" system that centralizes user data and dynamically generates professional, ATS-optimized PDF resumes. By streamlining the search process and automating resume creation, SmartJob Aggregator significantly reduces the friction of job hunting, allowing candidates to focus on preparation rather than administration.
    """
    story.append(Paragraph(abstract_text, body_style))

    # Technologies Used
    story.append(Paragraph("Technologies & Tools", heading_style))
    
    tech_data = [
        ["User Interface (Frontend)", "Next.js 14, React, TypeScript, Tailwind CSS"],
        ["Backend API", "FastAPI (Python), Pydantic"],
        ["Database", "SQLAlchemy ORM (SQLite/PostgreSQL)"],
        ["PDF Generation", "ReportLab, PyPDF2"],
        ["Authentication", "JWT (JSON Web Tokens), BCrypt"],
        ["Data Processing", "BeautifulSoup (Web Scraping)"]
    ]
    
    t = Table(tech_data, colWidths=[2.5*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), # Bold first column
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
    ]))
    story.append(t)

    # Key Features
    story.append(Paragraph("Key Features", heading_style))
    features = [
        "<b>Aggregated Job Search:</b> Real-time job listings from multiple major platforms in one tailored feed.",
        "<b>Smart Profile Management:</b> Deeply structured user profiles (Education, Projects, Experience) that serve as a single source of truth.",
        "<b>Dynamic Resume Builder:</b> One-click generation of ATS-friendly PDF resumes (Modern & Classic templates) with neat bullet points and optimized executive summaries.",
        "<b>Secure Authentication:</b> Robust user security with encrypted passwords and token-based sessions.",
        "<b>Responsive Design:</b> A premium, accessible dark-mode UI that works seamlessly across desktop and mobile devices."
    ]
    
    bullet_list = []
    for f in features:
        bullet_list.append(ListItem(Paragraph(f, body_style), bulletColor=colors.black, value='circle'))
    
    story.append(ListFlowable(bullet_list, bulletType='bullet', start='bulletchar', leftIndent=10))

    # Conclusion
    story.append(Paragraph("Conclusion", heading_style))
    conclusion = """
    SmartJob Aggregator successfully modernizes the job application lifecycle. By combining powerful aggregation algorithms with automated document generation, it serves as a comprehensive career assistant that empowers users to present their best selves to potential employers with minimal effort.
    """
    story.append(Paragraph(conclusion, body_style))

    doc.build(story)
    print("Abstract PDF generated successfully: SmartJob_Aggregator_Abstract.pdf")

if __name__ == "__main__":
    generate_abstract()
