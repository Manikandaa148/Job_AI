from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import json

# PDF Generation Imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import PyPDF2

import models
import schemas
import auth
import resume_analyzer
from database import engine, get_db
from scrapers.google_search import search_jobs_google

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Aggregator API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Job Aggregator API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/search", response_model=List[schemas.Job])
def search_jobs(request: schemas.JobSearchRequest):
    # Append company size to query if present
    query = request.query
    if request.company_size:
        size_map = {
            "Startup": "Startup",
            "Small": "Small company",
            "Mid-size": "Mid-size company",
            "Large": "Large company",
            "MNC": "MNC"
        }
        # Map selected sizes to keywords
        keywords = [size_map.get(s, s) for s in request.company_size]
        # Add to query
        size_query = " OR ".join(keywords)
        query = f"{query} {size_query}"

    jobs = search_jobs_google(
        query, 
        request.location, 
        request.start,
        experience_level=request.experience_level,
        platforms=request.platforms
    )
    return jobs

# Auth Endpoints
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.UserResponse)
def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    print(f"--- Updating user profile for: {current_user.email} ---")
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
        print(f"Updated full_name: {user_update.full_name}")
    if user_update.address is not None:
        current_user.address = user_update.address
        print(f"Updated address: {user_update.address}")
    if user_update.location is not None:
        current_user.location = user_update.location
        print(f"Updated location: {user_update.location}")
    if user_update.experience_level is not None:
        current_user.experience_level = user_update.experience_level
        print(f"Updated experience_level: {user_update.experience_level}")
    if user_update.skills is not None:
        current_user.skills = user_update.skills
        print(f"Updated skills: {user_update.skills}")
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar
        print(f"Updated avatar: {user_update.avatar[:50]}..." if len(user_update.avatar) > 50 else f"Updated avatar: {user_update.avatar}")
    if user_update.education is not None:
        current_user.education = user_update.education
        print(f"Updated education: {len(user_update.education)} items")
    if user_update.experience is not None:
        current_user.experience = user_update.experience
        print(f"Updated experience: {len(user_update.experience)} items")
    if user_update.job_preferences is not None:
        current_user.job_preferences = user_update.job_preferences
        print(f"Updated job_preferences: {user_update.job_preferences}")
    if user_update.projects is not None:
        current_user.projects = user_update.projects
        print(f"Updated projects: {len(user_update.projects)} items")
        
    db.commit()
    db.refresh(current_user)
    print(f"--- Profile updated successfully ---")
    print(f"Final education count: {len(current_user.education)}")
    print(f"Final experience count: {len(current_user.experience)}")
    print(f"Final projects count: {len(current_user.projects)}")
    return current_user

SKILL_KNOWLEDGE_BASE = {
    "Frontend Developer": ["React", "TypeScript", "Tailwind CSS", "Next.js", "Redux", "Web Performance"],
    "Backend Developer": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "System Design"],
    "Full Stack Developer": ["React", "Node.js", "Python", "Database Design", "DevOps", "GraphQL"],
    "Data Scientist": ["Python", "Pandas", "Machine Learning", "SQL", "TensorFlow", "Statistics"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Linux"],
    "Product Manager": ["Agile", "User Research", "Roadmapping", "Data Analysis", "Communication"],
    "Mobile Developer": ["React Native", "Flutter", "iOS", "Android", "Dart"],
}

@app.get("/recommendations")
def get_recommendations(current_user: models.User = Depends(auth.get_current_user)):
    """Suggests skills based on user's job preferences and missing skills."""
    user_skills = set(s.lower() for s in current_user.skills)
    recommendations = []
    
    # Analyze based on job preferences
    if current_user.job_preferences:
        for pref in current_user.job_preferences:
            print(f"Checking preference: {pref}")
            # Simple keyword matching
            for role, required_skills in SKILL_KNOWLEDGE_BASE.items():
                if role.lower() in pref.lower() or pref.lower() in role.lower():
                    for skill in required_skills:
                        if skill.lower() not in user_skills:
                            recommendations.append({
                                "skill": skill,
                                "role": role,
                                "reason": f"Recommended for {role} roles"
                            })
                            
    # Fallback to general based on missing basics if list is empty
    if not recommendations:
        # Check experience level
        if current_user.experience_level == "Fresher":
             recommendations.append({"skill": "Git", "role": "General", "reason": "Essential for all developers"})
             recommendations.append({"skill": "Communication", "role": "General", "reason": "Key soft skill"})

    # Deduplicate by skill name
    unique_recommendations = {}
    for rec in recommendations:
        if rec['skill'] not in unique_recommendations:
            unique_recommendations[rec['skill']] = rec
            
    return list(unique_recommendations.values())

@app.get("/suggestions")
def get_suggestions(type: str, query: str = ""):
    """Get autocomplete suggestions for various fields"""
    import suggestions as sug
    
    query_lower = query.lower()
    
    if type == "job":
        results = [job for job in sug.POPULAR_JOB_TITLES if query_lower in job.lower()]
    elif type == "location":
        results = [loc for loc in sug.POPULAR_LOCATIONS if query_lower in loc.lower()]
    elif type == "skill":
        results = [skill for skill in sug.POPULAR_SKILLS if query_lower in skill.lower()]
    elif type == "university":
        results = [uni for uni in sug.POPULAR_UNIVERSITIES if query_lower in uni.lower()]
    elif type == "company":
        results = [comp for comp in sug.POPULAR_COMPANIES if query_lower in comp.lower()]
    elif type == "degree":
        results = [deg for deg in sug.DEGREE_TYPES if query_lower in deg.lower()]
    elif type == "field":
        results = [field for field in sug.FIELDS_OF_STUDY if query_lower in field.lower()]
    else:
        results = []
    
    # Return top 10 matches
    return results[:10]

@app.post("/analyze-resume-file")
async def analyze_resume_file(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    """Analyze an uploaded resume file (PDF only for now) and return an ATS score"""
    
    extracted_text = ""
    try:
        content = await file.read()
        
        if file.filename.endswith('.pdf'):
            pdf_file = io.BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        else:
             # Basic fallback for text/other files if needed, or just error
             raise HTTPException(status_code=400, detail="Only PDF files are supported for analysis currently")
             
    except Exception as e:
        print(f"Error reading resume file analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to process file")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    analysis = resume_analyzer.analyze_resume_text(extracted_text)
    return analysis

@app.post("/generate-resume")
async def generate_resume_endpoint(
    resume_file: Optional[UploadFile] = File(None),
    template_id: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user)
):
    print(f"\n=== PDF GENERATION STARTED ===")
    print(f"User: {current_user.email}")
    print(f"Template: {template_id}")
    print(f"Full Name: {current_user.full_name}")
    print(f"Skills: {current_user.skills}")
    print(f"Education items: {len(current_user.education)}")
    print(f"Experience items: {len(current_user.experience)}")
    print(f"Projects items: {len(current_user.projects)}")
    
    # 1. Extract Text from Uploaded PDF (if any)
    extracted_text = ""
    if resume_file:
        try:
            content = await resume_file.read()
            pdf_file = io.BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            print(f"Extracted text length: {len(extracted_text)}")
        except Exception as e:
            print(f"Error reading resume file bytes: {e}")

    # 2. Setup PDF Document
    buffer = io.BytesIO()
    
    # Adjust margins based on template for maximum space
    # Modern typically needs less margin to look "full"
    margins = 30 if template_id == 'modern' else 50
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=margins, leftMargin=margins, 
        topMargin=margins, bottomMargin=margins
    )
    
    styles = getSampleStyleSheet()
    Story = []

    # 3. Helper Functions for Styles
    def get_styles(t_id):
        # Color Palettes
        colors_map = {
            'modern': {'primary': colors.HexColor('#2c3e50'), 'secondary': colors.HexColor('#34495e'), 'sidebar_bg': colors.HexColor('#f4f6f7')},
            'classic': {'primary': colors.HexColor('#0e4c92'), 'secondary': colors.black, 'undeline': True}, # Image 1 Style
            'minimal': {'primary': colors.black, 'secondary': colors.darkgray},
            'creative': {'primary': colors.HexColor('#7c3aed'), 'secondary': colors.HexColor('#4c1d95')}, # Image 2 Right
            'executive': {'primary': colors.HexColor('#1a1a1a'), 'secondary': colors.HexColor('#444444')}
        }
        c = colors_map.get(t_id, colors_map['classic'])
        
        # Base Styles
        s = {
            'title': ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=c['primary'], spaceAfter=10),
            'header': ParagraphStyle('Header', parent=styles['Heading2'], fontSize=14, textColor=c['primary'], spaceBefore=12, spaceAfter=6),
            'body': ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=colors.black, leading=14),
            'small': ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#555555'), leading=11),
        }
        
        if t_id == 'modern':
            s['title'].fontName = 'Helvetica-Bold'
            s['header'].textTransform = 'uppercase'
        elif t_id == 'classic':
            s['title'].fontName = 'Times-Bold'
            s['title'].alignment = 1 # Center
            s['header'].fontName = 'Helvetica-Bold'
            # Add underline to header for Classic
            s['header'].borderWidth = 1
            s['header'].borderColor = c['primary']
            s['header'].borderPadding = 5
            s['header'].borderRadius = 0
            # Note: Paragraph borders in simple ReportLab styles are tricky, usually done with Table or LineDrawing.
            # We'll stick to color and font for now, and add lines via Flowables if needed.
        elif t_id == 'creative':
            s['title'].fontName = 'Helvetica-Bold'
            s['title'].alignment = 1 # Center
            s['title'].textColor = c['primary']
            s['header'].textColor = c['primary']
            s['header'].alignment = 1 # Center

        return s

    style_map = get_styles(template_id)

    # 4. Generate Executive Summary
    def generate_executive_summary():
        """Generate a 6-line executive summary based on user's profile"""
        lines = []
        
        # Line 1: Professional title and experience level
        exp_level = current_user.experience_level or "Professional"
        job_pref = current_user.job_preferences[0] if current_user.job_preferences else "Software Professional"
        lines.append(f"{exp_level} {job_pref} with a proven track record of delivering high-quality solutions.")
        
        # Line 2: Years of experience and key strength
        if current_user.experience:
            years_exp = len(current_user.experience)
            if years_exp > 0:
                lines.append(f"Over {years_exp}+ years of hands-on experience in software development and technical leadership.")
            else:
                lines.append("Passionate about technology with strong foundation in software development principles.")
        else:
            lines.append("Dedicated professional with strong analytical and problem-solving capabilities.")
        
        # Line 3: Technical expertise
        if current_user.skills and len(current_user.skills) >= 3:
            top_skills = ", ".join(current_user.skills[:3])
            lines.append(f"Expert in {top_skills}, with deep understanding of modern development practices.")
        else:
            lines.append("Proficient in multiple programming languages and frameworks with focus on best practices.")
        
        # Line 4: Project/Achievement focus
        if current_user.projects and len(current_user.projects) > 0:
            lines.append(f"Successfully delivered {len(current_user.projects)}+ projects, demonstrating strong project management and execution skills.")
        elif current_user.experience and len(current_user.experience) > 0:
            lines.append("Demonstrated ability to lead cross-functional teams and deliver complex technical solutions.")
        else:
            lines.append("Strong track record of contributing to innovative projects and driving technical excellence.")
        
        # Line 5: Education and continuous learning
        if current_user.education and len(current_user.education) > 0:
            edu = current_user.education[0]
            school = edu.get('school', 'prestigious institution')
            lines.append(f"Holds degree from {school}, committed to continuous learning and professional development.")
        else:
            lines.append("Committed to continuous learning and staying updated with latest industry trends and technologies.")
        
        # Line 6: Career goals and value proposition
        if current_user.job_preferences:
            lines.append(f"Seeking opportunities to leverage expertise and drive innovation in challenging environments.")
        else:
            lines.append("Ready to contribute technical expertise and leadership to drive organizational success.")
        
        return " ".join(lines)

    # 5. Content Construction Functions
    
    def build_classic_layout():
        """Single column, Centered Header, Blue Accents (Image 1)"""
        # Header
        Story.append(Paragraph(current_user.full_name or "Your Name", style_map['title']))
        
        contact_parts = [
            current_user.email,
            getattr(current_user, 'address', '') or '',
            getattr(current_user, 'location', '') or ''
        ]
        linkedin = getattr(current_user, 'linkedin_url', None)
        if linkedin: contact_parts.append(linkedin)
        
        contact = " | ".join(filter(None, contact_parts))
        Story.append(Paragraph(contact, ParagraphStyle('CenterSmall', parent=style_map['small'], alignment=1)))
        Story.append(Spacer(1, 20))

        # Dynamic Sections
        
        # 1. Executive Summary (Dynamic 6-line summary)
        summary_text = generate_executive_summary()
        
        Story.append(Paragraph('Executive Summary', style_map['header']))
        line_color = style_map['header'].textColor
        Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
        Story.append(Spacer(1, 10))
        Story.append(Paragraph(summary_text, style_map['body']))
        Story.append(Spacer(1, 10))

        # 2. Skills
        if current_user.skills:
            Story.append(Paragraph('Technical Skills', style_map['header']))
            Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
            Story.append(Spacer(1, 10))
            Story.append(Paragraph(f"<b>Core Skills:</b> {', '.join(current_user.skills)}", style_map['body']))
            Story.append(Spacer(1, 10))

        # 3. Experience
        if current_user.experience:
            Story.append(Paragraph('Experience', style_map['header']))
            Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
            Story.append(Spacer(1, 10))
            for exp in current_user.experience:
                title_line = f"<b>{exp.get('role', 'Role')}</b> – {exp.get('company', 'Company')}"
                if exp.get('location'):
                    title_line += f" ({exp.get('location')})"
                Story.append(Paragraph(title_line, style_map['body']))
                
                date_line = f"<i>{exp.get('startDate', '')} - {exp.get('endDate', 'Present')}</i>"
                Story.append(Paragraph(date_line, style_map['small']))
                
                if exp.get('description'):
                    Story.append(Paragraph(exp.get('description'), style_map['body']))
                Story.append(Spacer(1, 10))

        # 4. Education
        if current_user.education:
            Story.append(Paragraph('Education', style_map['header']))
            Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
            Story.append(Spacer(1, 10))
            for edu in current_user.education:
                Story.append(Paragraph(f"<b>{edu.get('degree', 'Degree')}</b> in {edu.get('field', 'Field')}", style_map['body']))
                Story.append(Paragraph(f"{edu.get('school', 'School')}, {edu.get('startDate', '')} - {edu.get('endDate', '')}", style_map['small']))
                if edu.get('grade'):
                     Story.append(Paragraph(f"Grade: {edu.get('grade')}", style_map['small']))
                Story.append(Spacer(1, 6))

        # 5. Projects
        if current_user.projects:
            Story.append(Paragraph('Projects', style_map['header']))
            Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
            Story.append(Spacer(1, 10))
            for project in current_user.projects:
                title_line = f"<b>{project.get('name', 'Project Name')}</b>"
                if project.get('role'):
                    title_line += f" – {project.get('role')}"
                Story.append(Paragraph(title_line, style_map['body']))
                
                if project.get('duration'):
                    Story.append(Paragraph(f"<i>{project.get('duration')}</i>", style_map['small']))
                
                if project.get('technologies'):
                    tech_list = project.get('technologies') if isinstance(project.get('technologies'), str) else ', '.join(project.get('technologies', []))
                    Story.append(Paragraph(f"Technologies: {tech_list}", style_map['small']))
                
                if project.get('description'):
                    Story.append(Paragraph(project.get('description'), style_map['body']))
                
                if project.get('link'):
                    Story.append(Paragraph(f"Link: {project.get('link')}", style_map['small']))
                
                Story.append(Spacer(1, 10))

        if extracted_text:
            Story.append(Paragraph("Extracted Content", style_map['header']))
            Story.append(Paragraph(extracted_text[:2000].replace('\n', '<br/>'), style_map['small']))


    def build_modern_layout():
        """Two Column Layout (Image 2 Left)"""
        # Create data for a big 2-column table
        # Left Col: Contact, Skills, Langs
        # Right Col: Profile, Exp, Edu, Projects
        
        # Styles for Sidebar
        sidebar_style = ParagraphStyle('Sidebar', parent=style_map['body'], fontSize=9, leading=12)
        sidebar_header = ParagraphStyle('SidebarHeader', parent=style_map['header'], fontSize=11, spaceBefore=10)
        
        # Left Column Content
        left_content = []
        left_content.append(Paragraph("<b>CONTACT</b>", sidebar_header))
        left_content.append(Paragraph(current_user.email, sidebar_style))
        if getattr(current_user, 'address', None): left_content.append(Paragraph(current_user.address, sidebar_style))
        if getattr(current_user, 'location', None): left_content.append(Paragraph(current_user.location, sidebar_style))
        if getattr(current_user, 'linkedin_url', None): left_content.append(Paragraph(f"LinkedIn: {current_user.linkedin_url}", sidebar_style))
        left_content.append(Spacer(1, 15))
        
        left_content.append(Paragraph("<b>SKILLS</b>", sidebar_header))
        if current_user.skills:
            for skill in current_user.skills:
                left_content.append(Paragraph(f"• {skill}", sidebar_style))
        else:
             left_content.append(Paragraph("No skills listed", sidebar_style))
        
        left_content.append(Spacer(1, 15))
        
        if current_user.education:
            left_content.append(Paragraph("<b>EDUCATION</b>", sidebar_header))
            for edu in current_user.education:
                left_content.append(Paragraph(f"<b>{edu.get('degree', 'Degree')}</b>", sidebar_style))
                left_content.append(Paragraph(edu.get('school', 'School'), sidebar_style))
                left_content.append(Paragraph(f"{edu.get('startDate', '')}-{edu.get('endDate', '')}", sidebar_style))
                left_content.append(Spacer(1, 5))

        # Right Column Content
        right_content = []
        right_content.append(Paragraph(current_user.full_name or "Your Name", style_map['title']))
        right_content.append(Paragraph(f"<b>{getattr(current_user, 'experience_level', '') or 'Professional'}</b>", ParagraphStyle('RoleConfig', parent=style_map['body'], fontSize=12, textColor=colors.gray)))
        right_content.append(Spacer(1, 20))
        
        right_content.append(Paragraph("PROFILE", style_map['header']))
        summary_text = generate_executive_summary()
        right_content.append(Paragraph(summary_text, style_map['body']))
        
        if current_user.experience:
            right_content.append(Paragraph("WORK EXPERIENCE", style_map['header']))
            for exp in current_user.experience:
                right_content.append(Paragraph(f"<b>{exp.get('role', 'Role')}</b>", style_map['body']))
                right_content.append(Paragraph(f"<i>{exp.get('company', 'Company')} | {exp.get('startDate', '')} - {exp.get('endDate', 'Present')}</i>", style_map['small']))
                if exp.get('description'):
                    right_content.append(Paragraph(f"• {exp.get('description')}", style_map['body']))
                right_content.append(Spacer(1, 10))
        
        if current_user.projects:
            right_content.append(Paragraph("PROJECTS", style_map['header']))
            for project in current_user.projects:
                right_content.append(Paragraph(f"<b>{project.get('name', 'Project Name')}</b>", style_map['body']))
                
                details = []
                if project.get('role'):
                    details.append(project.get('role'))
                if project.get('duration'):
                    details.append(project.get('duration'))
                if details:
                    right_content.append(Paragraph(f"<i>{' | '.join(details)}</i>", style_map['small']))
                
                if project.get('technologies'):
                    tech_list = project.get('technologies') if isinstance(project.get('technologies'), str) else ', '.join(project.get('technologies', []))
                    right_content.append(Paragraph(f"Tech: {tech_list}", style_map['small']))
                
                if project.get('description'):
                    right_content.append(Paragraph(f"• {project.get('description')}", style_map['body']))
                
                right_content.append(Spacer(1, 10))
        
        if extracted_text:
             right_content.append(Paragraph("EXTRACTED", style_map['header']))
             right_content.append(Paragraph(extracted_text[:1000].replace('\n', '<br/>'), style_map['small']))

        # Table for Layout
        col1_width = 160
        col2_width = 390
        
        t = Table(
            [[left_content, right_content]], 
            colWidths=[col1_width, col2_width],
            style=[
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (0,0), 0),
                ('RIGHTPADDING', (0,0), (0,0), 10),
                ('LEFTPADDING', (1,0), (1,0), 20),
                ('LINEBEFORE', (1,0), (1,0), 0.5, colors.lightgrey), # Vertical Separator
            ]
        )
        Story.append(t)

    # 5. Select Layout Builder & 6. Build
    try:
        if template_id == 'modern':
            build_modern_layout()
        else:
            build_classic_layout()

        doc.build(Story)
        buffer.seek(0)
        print(f"--- SUCCESS: PDF Built. Size: {buffer.getbuffer().nbytes} bytes ---")
        return StreamingResponse(
            buffer, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=resume_{template_id}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error building PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF Generation Failed: {str(e)}")
