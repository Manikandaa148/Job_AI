import re

def analyze_resume_text(text: str) -> dict:
    score = 0
    max_score = 100
    breakdown = []
    
    # Normalize text
    text_lower = text.lower()
    
    # 1. Contact Information (10 points)
    # Check for email
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
        score += 5
    else:
        breakdown.append("Missing email address")
        
    # Check for phone (simple pattern)
    if re.search(r'\d{10}|\d{3}[-\.\s]\d{3}[-\.\s]\d{4}', text):
        score += 5
    else:
        breakdown.append("Missing phone number")

    # 2. Key Sections Detection (40 points)
    sections = {
        "experience": ["experience", "work history", "employment"],
        "education": ["education", "academic", "university", "college", "school"],
        "skills": ["skills", "technologies", "technical proficiency", "competencies"],
        "projects": ["projects", "personal projects", "portfolio"]
    }
    
    for section, keywords in sections.items():
        if any(k in text_lower for k in keywords):
            score += 10
        else:
            breakdown.append(f"Missing '{section.capitalize()}' section")

    # 3. Content Length/Depth (20 points)
    word_count = len(text.split())
    if word_count > 1000:
        score += 20
    elif word_count > 400:
        score += 15
    elif word_count > 200:
        score += 10
        breakdown.append("Resume is a bit short, aim for 400+ words")
    else:
        score += 5
        breakdown.append("Resume is too short, add more details")

    # 4. Measurable Results (Keywords) (15 points)
    # Look for action verbs and metrics
    metrics = ["%", "$", "increased", "decreased", "improved", "reduced", "led", "managed", "developed", "created"]
    metric_count = sum(1 for m in metrics if m in text_lower)
    
    if metric_count >= 5:
        score += 15
    elif metric_count >= 2:
        score += 10
        breakdown.append("Use more action verbs and metrics (e.g. %, $)")
    else:
        breakdown.append("Add measurable results (numbers, metrics) to your experience")

    # 5. File Format/Readability (15 points)
    # If we extracted text successfully, that's a good sign.
    score += 15

    return {
        "score": min(score, 100),
        "breakdown": breakdown
    }
