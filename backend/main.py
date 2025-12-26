from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import io
import json
import os
import shutil

load_dotenv()

# PDF Generation Imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import PyPDF2
import random

import models
import schemas
import auth
import resume_analyzer
import chatbot
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

app.include_router(chatbot.router)

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
    
    # Log login activity
    try:
        from activity_logger import log_activity
        log_activity(user.email, "LOGIN", "User logged in successfully")
    except Exception as e:
        print(f"Logging failed: {e}")

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.UserResponse)
def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    print(f"--- Updating user profile for: {current_user.email} ---")
    
    changes = []
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
        changes.append("full_name")
    if user_update.address is not None:
        current_user.address = user_update.address
        changes.append("address")
    if user_update.location is not None:
        current_user.location = user_update.location
        changes.append("location")
    if user_update.experience_level is not None:
        current_user.experience_level = user_update.experience_level
        changes.append("experience_level")
    if user_update.total_experience is not None:
        current_user.total_experience = user_update.total_experience
        changes.append("total_experience")
    if user_update.skills is not None:
        current_user.skills = user_update.skills
        changes.append("skills")
    if user_update.preferred_locations is not None:
        current_user.preferred_locations = user_update.preferred_locations
        changes.append("preferred_locations")
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar
        changes.append("avatar")
    if user_update.education is not None:
        current_user.education = user_update.education
        changes.append("education")
    if user_update.experience is not None:
        current_user.experience = user_update.experience
        changes.append("experience")
    if user_update.job_preferences is not None:
        current_user.job_preferences = user_update.job_preferences
        changes.append("job_preferences")
    if user_update.projects is not None:
        current_user.projects = user_update.projects
        changes.append("projects")
    if user_update.linkedin_url is not None:
        current_user.linkedin_url = user_update.linkedin_url
        changes.append("linkedin_url")
    if user_update.github_url is not None:
        current_user.github_url = user_update.github_url
        changes.append("github_url")
    if user_update.portfolio_url is not None:
        current_user.portfolio_url = user_update.portfolio_url
        changes.append("portfolio_url")
        
    db.commit()
    db.refresh(current_user)
    
    # Log update activity
    try:
        from activity_logger import log_activity
        log_activity(current_user.email, "PROFILE_UPDATE", f"Updated fields: {', '.join(changes)}")
    except Exception as e:
        print(f"Logging failed: {e}")

    print(f"--- Profile updated successfully ---")
    return current_user

@app.get("/notifications")
def get_notifications(current_user: models.User = Depends(auth.get_current_user)):
    """
    Generate dynamic notifications based on user profile, skills, and preferences.
    """
    try:
        notifications = []
        
        # 1. Profile Completion Notification
        missing_fields = []
        try:
            if not current_user.linkedin_url: missing_fields.append("LinkedIn")
            if not current_user.github_url: missing_fields.append("GitHub")
        except Exception as e:
            print(f"Error checking profile fields: {e}")
        
        if missing_fields:
            notifications.append({
                "id": "profile-incomplete",
                "type": "alert",
                "title": "Profile Incomplete",
                "message": f"Add {', '.join(missing_fields)} to boost your profile visibility.",
                "action_label": "Update Profile",
                "action_link": "?modal=profile" # Frontend sets specific query param or state
            })

        # 2. Resume & Analysis Notification
        try:
            # Check if user has uploaded a resume to profile
            has_resume = hasattr(current_user, 'resume_path') and current_user.resume_path
            
            # Check if user has an analysis score
            has_analysis = hasattr(current_user, 'resume_score') and current_user.resume_score is not None
            
            if has_analysis:
                score = current_user.resume_score
                msg = "Your resume score is great!" if score > 70 else "Your resume needs same improvement."
                notifications.append({
                    "id": "resume-score",
                    "type": "alert" if score < 70 else "success",
                    "title": f"Resume Score: {score}/100",
                    "message": msg,
                    "action_label": "Analyze Again",
                    "action_link": "?modal=resume_builder"
                })
            elif has_resume:
                # Resume uploaded but not analyzed (or old score logic)
                notifications.append({
                    "id": "resume-analyze",
                    "type": "info",
                    "title": "Analyze Your Resume",
                    "message": "You have a resume saved. Get an AI analysis score now.",
                    "action_label": "Analyze Now",
                    "action_link": "?modal=resume_builder"
                })
            else:
                # No resume at all
                notifications.append({
                    "id": "resume-missing",
                    "type": "info",
                    "title": "Upload Your Resume",
                    "message": "Upload your resume to your profile to get started.",
                    "action_label": "Upload Resume",
                    "action_link": "?modal=profile"
                })
        except Exception as e:
            print(f"Error checking resume score: {e}")
        except Exception as e:
            print(f"Error checking resume score: {e}")

        # 3. Current Skills Highlight
        try:
            if current_user.skills and len(current_user.skills) > 0:
                top_skills = ", ".join(current_user.skills[:3])
                notifications.append({
                    "id": "your-skills",
                    "type": "success",
                    "title": "Your Top Skills",
                    "message": f"You are profiled as proficient in: {top_skills}. specific jobs are recommended based on this.",
                    "action_label": "View Profile",
                    "action_link": "?modal=profile"
                })
        except Exception as e:
            print(f"Error checking skills: {e}")

        # 4. Skill Recommendations (based on existing logic)
        try:
            recommendations = get_recommendations(current_user)
            if recommendations:
                top_rec = recommendations[0]
                notifications.append({
                    "id": f"skill-{top_rec['skill']}",
                    "type": "info",
                    "title": f"Recommended Skill: {top_rec['skill']}",
                    "message": "Source: Google Search",
                    "action_label": "Learn More",
                    "action_link": f"https://www.google.com/search?q=learn+{top_rec['skill']}"
                })
        except Exception as e:
             print(f"Error getting recommendations: {e}")

        # 5. Job Alerts
        try:
            if current_user.job_preferences and current_user.preferred_locations:
                role = current_user.job_preferences[0]
                loc = current_user.preferred_locations[0]
                notifications.append({
                    "id": "new-jobs",
                    "type": "success",
                    "title": "New Jobs Found",
                    "message": f"3 new {role} jobs in {loc} posted today.",
                    "action_label": "View Jobs",
                    "action_link": f"/?q={role}&location={loc}"
                })
            elif not current_user.job_preferences:
                notifications.append({
                    "id": "add-pref",
                    "type": "info",
                    "title": "Set Preferences",
                    "message": "Add job preferences to get personalized job alerts.",
                    "action_label": "Add Preference",
                    "action_link": "?modal=profile"
                })
        except Exception as e:
            print(f"Error checking job preferences: {e}")

        return notifications
        
    except Exception as e:
        print(f"CRITICAL ERROR in get_notifications: {e}")
        # Return empty list instead of crashing
        return []

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
async def analyze_resume_file(
    file: UploadFile = File(...), 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
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
             raise HTTPException(status_code=400, detail="Only PDF files are supported for analysis currently")
             
    except Exception as e:
        print(f"Error reading resume file analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to process file")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    analysis = resume_analyzer.analyze_resume_text(extracted_text)
    
    # Save score to user profile
    try:
        current_user.resume_score = analysis.get('score', 0)
        db.commit()
        db.refresh(current_user)
        print(f"Saved resume score {current_user.resume_score} for {current_user.email}")
    except Exception as e:
        print(f"Failed to save resume score: {e}")

    return analysis

    return analysis

@app.post("/users/me/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and store resume file for the user"""
    try:
        # Create uploads directory if not exists
        upload_dir = "uploads/resumes"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"user_{current_user.id}_resume{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update user profile
        current_user.resume_path = file_path
        db.commit()
        db.refresh(current_user)
        
        print(f"Resume saved to {file_path} for user {current_user.email}")
        return {"filename": file.filename, "path": file_path, "message": "Resume uploaded successfully"}
        
    except Exception as e:
        print(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload resume")


@app.post("/generate-resume")
async def generate_resume_endpoint(
    resume_file: Optional[UploadFile] = File(None),
    template_id: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user)
):
    print(f"\n=== PDF GENERATION STARTED ===")
    print(f"User: {current_user.email}")
    print(f"Template: {template_id}")
    
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
        except Exception as e:
            print(f"Error reading resume file bytes: {e}")

    # --- HELPER DATA & FUNCTIONS ---
    
    SKILL_CATEGORIES_MAPPING = {
        'Programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin', 'sql', 'mysql', 'nosql', 'mongodb', 'r', 'html', 'css', 'bash', 'shell'],
        'Libraries': ['react', 'angular', 'vue', 'next.js', 'node.js', 'django', 'fastapi', 'flask', 'spring', 'pandas', 'numpy', 'matplotlib', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv', 'jquery', 'bootstrap', 'tailwind css', 'redux'],
        'Tools': ['git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'jira', 'figma', 'postman', 'vscode', 'power bi', 'excel', 'tableau', 'spss', 'hadoop', 'spark', 'kafka', 'hive', 'maven', 'gradle', 'linux', 'unix'],
        'Concepts': ['agile', 'scrum', 'ci/cd', 'rest api', 'graphql', 'machine learning', 'deep learning', 'data structures', 'algorithms', 'system design', 'microservices', 'oop', 'functional programming', 'data cleaning', 'data visualization', 'statistical analysis', 'hypothesis testing', 'web development', 'cloud computing']
    }

    ROLE_DESCRIPTIONS = {
        'developer': [
            "Designed and implemented scalable code modules using best practices, ensuring high performance and maintainability.",
            "Participated in rigorous code reviews and contributed to continuous integration pipelines to maintain code quality.",
            "Collaborated with cross-functional teams to integrate third-party APIs and enhance application functionality."
        ],
        'engineer': [
            "Architected and developed robust software solutions to address complex technical challenges and business needs.",
            "Optimized system/application performance, resulting in reduced latency and improved user experience.",
            "Implemented automated testing frameworks and CI/CD pipelines to ensure reliable and rapid deployment."
        ],
        'analyst': [
            "Analyzed large, complex datasets to extract actionable insights and drive strategic business decisions.",
            "Created comprehensive dashboards and visualization reports to monitor key performance indicators (KPIs).",
            "Collaborated with stakeholders to identify data requirements and deliver analytical solutions that improved operational efficiency."
        ],
        'manager': [
            "Led and mentored a high-performing team of professionals, fostering a culture of collaboration and continuous improvement.",
            "Defined project roadmaps, managed resources, and ensured timely delivery of projects within scope and budget.",
            "Communicated project status, risks, and opportunities to senior leadership and stakeholders effectively."
        ],
        'generic': [
            "Collaborated with cross-functional teams to define, design, and ship new features.",
            "Ensured the performance, quality, and responsiveness of applications through rigorous testing and optimization.",
            "Identified and corrected bottlenecks and fixed bugs to improve overall application stability."
        ]
    }

    def generate_work_description(role, company):
        role_lower = role.lower() if role else ""
        if any(x in role_lower for x in ['analyst', 'data', 'scientist']):
            return ROLE_DESCRIPTIONS['analyst']
        elif any(x in role_lower for x in ['manager', 'lead', 'head', 'director']):
            return ROLE_DESCRIPTIONS['manager']
        elif 'engineer' in role_lower:
            return ROLE_DESCRIPTIONS['engineer']
        elif any(x in role_lower for x in ['developer', 'programmer', 'coder']):
            return ROLE_DESCRIPTIONS['developer']
        else:
            return ROLE_DESCRIPTIONS['generic']

    def categorize_skills(skills_list):
        categorized = {k: [] for k in SKILL_CATEGORIES_MAPPING}
        used_skills = set()
        
        # 1. Exact/Partial Match for known categories
        for skill in skills_list:
            skill_lower = skill.lower()
            found = False
            for category, keywords in SKILL_CATEGORIES_MAPPING.items():
                if skill_lower in keywords: # Exact match preference
                    categorized[category].append(skill)
                    used_skills.add(skill)
                    found = True
                    break
            
            if not found:
                 for category, keywords in SKILL_CATEGORIES_MAPPING.items():
                    # Check if skill contains keyword (e.g. "React Native" contains "React")
                    if any(k in skill_lower for k in keywords): 
                        categorized[category].append(skill)
                        used_skills.add(skill)
                        found = True
                        break
        
        # 2. Put remaining in Tools or Concepts based on heuristic or default to Tools
        for skill in skills_list:
            if skill not in used_skills:
                # Fallback to Tools
                categorized['Tools'].append(skill)

        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}

    # 2. Setup PDF Document
    buffer = io.BytesIO()
    
    # optimize margins for single page
    margins = 0.5 * inch 
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
            'classic': {'primary': colors.HexColor('#0e4c92'), 'secondary': colors.black, 'undeline': True},
            'minimal': {'primary': colors.black, 'secondary': colors.darkgray},
            'creative': {'primary': colors.HexColor('#7c3aed'), 'secondary': colors.HexColor('#4c1d95')},
            'executive': {'primary': colors.HexColor('#1a1a1a'), 'secondary': colors.HexColor('#444444')}
        }
        c = colors_map.get(t_id, colors_map['classic'])
        
        # Base Styles
        s = {
            'title': ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=c['primary'], spaceAfter=6),
            'header': ParagraphStyle('Header', parent=styles['Heading2'], fontSize=12, textColor=c['primary'], spaceBefore=8, spaceAfter=4),
            'body': ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, textColor=colors.black, leading=12),
            'small': ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#555555'), leading=10),
            'list_item': ParagraphStyle('ListItem', parent=styles['Normal'], fontSize=9, textColor=colors.black, leading=12, leftIndent=10),
        }
        
        if t_id == 'modern':
            s['title'].fontName = 'Helvetica-Bold'
            s['header'].textTransform = 'uppercase'
        elif t_id == 'classic':
            s['title'].fontName = 'Times-Bold'
            # s['title'].alignment = 1 # Center - Keep Left for compact
            s['header'].fontName = 'Helvetica-Bold'
            s['header'].borderWidth = 0.5 # Thinner border
            s['header'].borderColor = c['primary']
            s['header'].borderPadding = 2
            s['header'].borderRadius = 0
            
        elif t_id == 'creative':
            s['title'].fontName = 'Helvetica-Bold'
            s['title'].alignment = 1 # Center
            s['title'].textColor = c['primary']
            s['header'].textColor = c['primary']
            s['header'].alignment = 1 # Center

        return s

    style_map = get_styles(template_id)

    # 4. Generate Executive Summary (Optimized for 4-5 neat lines)
    def generate_executive_summary():
        """Generate a neat 4-5 line executive summary based on user's profile"""
        
        role = current_user.job_preferences[0] if current_user.job_preferences else "Software Professional"
        exp_level = current_user.experience_level or "Experienced"
        years_exp = len(current_user.experience) if current_user.experience else 0
        
        summary_sentences = []
        
        # 1. Identity
        if years_exp > 0:
            summary_sentences.append(f"{exp_level} {role} with over {years_exp}+ years of experience in designing and implementing scalable software solutions.")
        else:
            summary_sentences.append(f"Motivated {role} with a strong academic background and deep passion for technology and software development.")
            
        # 2. Competencies
        if current_user.skills:
            top_skills = ", ".join(current_user.skills[:5])
            summary_sentences.append(f"Proficient in {top_skills}, utilizing modern best practices to deliver high-performance applications.")
        else:
            summary_sentences.append("Proficient in modern development methodologies with a focus on writing clean, maintainable code.")
            
        # 3. Achievements
        if current_user.projects and len(current_user.projects) > 0:
            summary_sentences.append(f"Successfully delivered {len(current_user.projects)} key projects, demonstrating exceptional problem-solving abilities and attention to detail.")
        elif current_user.experience:
             summary_sentences.append("Proven track record of collaborating with cross-functional teams to drive project success and innovation.")
        else:
             summary_sentences.append("Demonstrated ability to learn new technologies quickly and apply them to solve complex technical challenges.")

        # 4. Goal
        summary_sentences.append(f"Committed to continuous learning and leveraging expertise to contribute effectively to organizational growth while upholding high standards of quality. Strong communicator and team player, ready to take on challenging roles in a dynamic environment.")

        # Return combined string
        return " ".join(summary_sentences)

    # 5. Content Construction Functions
    
    def build_classic_layout():
        """Single column, No Photo, Bullets for Skills/Projects"""
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

        # 1. Executive Summary
        summary_text = generate_executive_summary()
        
        Story.append(Paragraph('Executive Summary', style_map['header']))
        line_color = style_map['header'].textColor
        Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
        Story.append(Spacer(1, 10))
        Story.append(Paragraph(summary_text, style_map['body']))
        Story.append(Spacer(1, 10))

        # 2. Skills (Categorized)
        if current_user.skills:
            Story.append(Paragraph('Technical Skills', style_map['header']))
            Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 0.5, line_color)]))
            Story.append(Spacer(1, 4))
            
            categorized_skills = categorize_skills(current_user.skills)
            
            # Define specific order
            order = ['Programming', 'Libraries', 'Tools', 'Concepts']
            
            for cat in order:
                if cat in categorized_skills:
                    skills_str = ", ".join(categorized_skills[cat])
                    # Bold Category Name
                    text = f"<b>{cat}:</b> {skills_str}"
                    Story.append(Paragraph(text, style_map['body']))
            
            # Add any others not in the main 4 if needed (though map covers all)
            for cat, skills in categorized_skills.items():
                if cat not in order:
                    skills_str = ", ".join(skills)
                    text = f"<b>{cat}:</b> {skills_str}"
                    Story.append(Paragraph(text, style_map['body']))
                    
            Story.append(Spacer(1, 6))

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
                
                if exp.get('description') and len(exp.get('description')) > 15:
                    Story.append(Paragraph(exp.get('description'), style_map['body']))
                else:
                    # Auto-generate description if missing or too short
                    gen_desc = generate_work_description(exp.get('role'), exp.get('company'))
                    bullets = []
                    for point in gen_desc:
                         bullets.append(ListItem(Paragraph(point, style_map['body']), bulletColor=colors.black, value='circle'))
                    Story.append(ListFlowable(bullets, bulletType='bullet', start='bulletchar', leftIndent=10))
                    
                Story.append(Spacer(1, 6))

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

        # 5. Projects (Bulleted)
        if current_user.projects:
            Story.append(Paragraph('Projects', style_map['header']))
            Story.append(Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 1, line_color)]))
            Story.append(Spacer(1, 10))
            
            for project in current_user.projects:
                title_line = f"<b>{project.get('name', 'Project Name')}</b>"
                if project.get('role'):
                    title_line += f" – {project.get('role')}"
                Story.append(Paragraph(title_line, style_map['body']))
                
                meta_parts = []
                if project.get('duration'): meta_parts.append(project.get('duration'))
                if project.get('link'): meta_parts.append(f"Link: {project.get('link')}")
                if meta_parts:
                    Story.append(Paragraph(" | ".join(meta_parts), style_map['small']))

                proj_bullets = []
                if project.get('description'):
                    proj_bullets.append(ListItem(Paragraph(f"Description: {project.get('description')}", style_map['body']), bulletColor=colors.black))
                if project.get('technologies'):
                    tech_list = project.get('technologies') if isinstance(project.get('technologies'), str) else ', '.join(project.get('technologies', []))
                    proj_bullets.append(ListItem(Paragraph(f"Tech Stack: {tech_list}", style_map['body']), bulletColor=colors.black))

                if proj_bullets:
                     Story.append(ListFlowable(proj_bullets, bulletType='bullet', start='bulletchar', leftIndent=10))
                
                Story.append(Spacer(1, 10))

        if extracted_text:
            Story.append(Paragraph("Extracted Content", style_map['header']))
            Story.append(Paragraph(extracted_text[:2000].replace('\n', '<br/>'), style_map['small']))


    def build_modern_layout():
        """Two Column Layout (No Photo)"""
        sidebar_style = ParagraphStyle('Sidebar', parent=style_map['body'], fontSize=9, leading=12)
        sidebar_header = ParagraphStyle('SidebarHeader', parent=style_map['header'], fontSize=11, spaceBefore=10)
        
        left_content = []
        left_content.append(Paragraph("<b>CONTACT</b>", sidebar_header))
        left_content.append(Paragraph(current_user.email, sidebar_style))
        if getattr(current_user, 'address', None): left_content.append(Paragraph(current_user.address, sidebar_style))
        if getattr(current_user, 'location', None): left_content.append(Paragraph(current_user.location, sidebar_style))
        if getattr(current_user, 'linkedin_url', None): left_content.append(Paragraph(f"LinkedIn: {current_user.linkedin_url}", sidebar_style))
        left_content.append(Spacer(1, 15))
        
        left_content.append(Paragraph("<b>SKILLS</b>", sidebar_header))
        categorized_skills = categorize_skills(current_user.skills)
        order = ['Programming', 'Libraries', 'Tools', 'Concepts']
        
        for cat in order:
            if cat in categorized_skills:
                left_content.append(Paragraph(f"<b>{cat}</b>", sidebar_style))
                for skill in categorized_skills[cat]:
                     left_content.append(Paragraph(f"• {skill}", sidebar_style))
                left_content.append(Spacer(1, 4))
        
        # Catch remaining
        for cat in categorized_skills:
            if cat not in order:
                left_content.append(Paragraph(f"<b>{cat}</b>", sidebar_style))
                for skill in categorized_skills[cat]:
                     left_content.append(Paragraph(f"• {skill}", sidebar_style))
                left_content.append(Spacer(1, 4))
        
        if not categorized_skills and not current_user.skills:
             left_content.append(Paragraph("No skills listed", sidebar_style))
        
        left_content.append(Spacer(1, 15))
        
        if current_user.education:
            left_content.append(Paragraph("<b>EDUCATION</b>", sidebar_header))
            for edu in current_user.education:
                left_content.append(Paragraph(f"<b>{edu.get('degree', 'Degree')}</b>", sidebar_style))
                left_content.append(Paragraph(edu.get('school', 'School'), sidebar_style))
                left_content.append(Paragraph(f"{edu.get('startDate', '')}-{edu.get('endDate', '')}", sidebar_style))
                left_content.append(Spacer(1, 5))

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
                
                if exp.get('description') and len(exp.get('description')) > 15:
                    desc = exp.get('description')
                    right_content.append(Paragraph(f"• {desc}", style_map['body']))
                else:
                    # Auto generate
                    gen_desc = generate_work_description(exp.get('role'), exp.get('company'))
                    for point in gen_desc:
                        right_content.append(Paragraph(f"• {point}", style_map['body']))
                        
                right_content.append(Spacer(1, 6))
        
        if current_user.projects:
            right_content.append(Paragraph("PROJECTS", style_map['header']))
            for project in current_user.projects:
                right_content.append(Paragraph(f"<b>{project.get('name', 'Project Name')}</b>", style_map['body']))
                
                details = []
                if project.get('role'): details.append(project.get('role'))
                if project.get('duration'): details.append(project.get('duration'))
                if details:
                    right_content.append(Paragraph(f"<i>{' | '.join(details)}</i>", style_map['small']))
                
                if project.get('technologies'):
                    tech_list = project.get('technologies') if isinstance(project.get('technologies'), str) else ', '.join(project.get('technologies', []))
                    right_content.append(Paragraph(f"• Tech: {tech_list}", style_map['small']))
                
                if project.get('description'):
                    right_content.append(Paragraph(f"• {project.get('description')}", style_map['body']))
                
                right_content.append(Spacer(1, 10))
        
        if extracted_text:
             right_content.append(Paragraph("EXTRACTED", style_map['header']))
             right_content.append(Paragraph(extracted_text[:1000].replace('\n', '<br/>'), style_map['small']))

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
                ('LINEBEFORE', (1,0), (1,0), 0.5, colors.lightgrey),
            ]
        )
        Story.append(t)

    try:
        if template_id == 'modern':
            build_modern_layout()
        else:
            build_classic_layout()

        doc.build(Story)
        buffer.seek(0)
        return StreamingResponse(
            buffer, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=resume_{template_id}.pdf"}
        )
    except Exception as e:
        print(f"Error building PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF Generation Failed: {str(e)}")

# --- Application Tracker Endpoints ---
@app.get("/applications", response_model=List[schemas.ApplicationResponse])
def get_applications(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all job applications for the current user"""
    return db.query(models.Application).filter(models.Application.user_id == current_user.id).order_by(models.Application.updated_at.desc()).all()

@app.post("/applications", response_model=schemas.ApplicationResponse)
def create_application(
    application: schemas.ApplicationCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Track a new job application"""
    db_application = models.Application(**application.dict(), user_id=current_user.id)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.put("/applications/{app_id}", response_model=schemas.ApplicationResponse)
def update_application(
    app_id: int,
    application: schemas.ApplicationUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update application status or notes"""
    db_app = db.query(models.Application).filter(models.Application.id == app_id, models.Application.user_id == current_user.id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status:
        db_app.status = application.status
    if application.notes is not None:
        db_app.notes = application.notes
        
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete("/applications/{app_id}")
def delete_application(
    app_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a tracked application"""
    db_app = db.query(models.Application).filter(models.Application.id == app_id, models.Application.user_id == current_user.id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    db.delete(db_app)
    db.commit()
    return {"message": "Application deleted successfully"}
