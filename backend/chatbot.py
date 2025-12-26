from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import google.generativeai as genai
from database import get_db
import models
import auth
import json
from scrapers.google_search import search_jobs_google

# Hardcoded rules for fallback when LLM is unavailable
SKILL_KNOWLEDGE_BASE = {
    "Frontend Developer": ["React", "TypeScript", "Tailwind CSS", "Next.js", "Redux", "Web Performance"],
    "Backend Developer": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "System Design"],
    "Full Stack Developer": ["React", "Node.js", "Python", "Database Design", "DevOps", "GraphQL"],
    "Data Scientist": ["Python", "Pandas", "Machine Learning", "SQL", "TensorFlow", "Statistics"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Linux"],
}

router = APIRouter(prefix="/chat", tags=["chatbot"])

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    reply: str

def get_user_context(user: models.User):
    context = f"User Name: {user.full_name}\n"
    context += f"Experience Level: {user.experience_level}\n"
    skills = ", ".join(user.skills) if user.skills else "Not specified"
    context += f"Skills: {skills}\n"
    
    # Add experience summary
    if user.experience:
        context += "Experience:\n"
        for exp in user.experience:
             context += f"- {exp.get('role')} at {exp.get('company')} ({exp.get('startDate')} - {exp.get('endDate')})\n"
    
    # Add education
    if user.education:
        context += "Education:\n"
        for edu in user.education:
            context += f"- {edu.get('degree')} in {edu.get('field')} at {edu.get('school')}\n"

    # Add preferences
    if user.job_preferences:
        prefs = ", ".join(user.job_preferences) if user.job_preferences else "None"
        context += f"Job Preferences: {prefs}\n"
        
    return context

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional),
    db: Session = Depends(get_db)
):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
         # Mock response if no key
         return ChatResponse(reply="I can help you with that, but first the developer needs to configure the GOOGLE_API_KEY in the backend environment variables to enable my AI brain!")

    genai.configure(api_key=api_key)

    try:
        # 1. Build Context
        if current_user:
            user_context = get_user_context(current_user)
            profile_str = f"USER PROFILE:\n{user_context}"
        else:
            profile_str = "USER PROFILE: Guest User (No profile data available). Ask them about their skills or experience to provide better advice."
        
        # 2. System Prompt
        system_instruction = f"""You are JobBot, an expert AI career counselor and recruiter assistant for the Job AI platform. 
        Your goal is to help the user with their job search, resume improvement, and interview preparation.
        
        {profile_str}
        
        INSTRUCTIONS:
        - Answer the user's question clearly and concisely in a natural, conversational tone.
        - You are "fully trained" to understand their profile. Use the profile data to personalize your advice.
        - If they ask for job recommendations, suggest specific job titles and industries that fit their skills and experience level.
        - If they ask about their resume, offer specific improvements based on their skills/experience.
        - Be encouraging and professional.
        """
        
        # 3. Model Init
        model = genai.GenerativeModel('gemini-pro-latest')
        
        # 4. Construct Chat History for Gemini
        gemini_history = []
        
        # Add system instruction as the first part of the conversation if possible, 
        # or prepending to the first user message. 
        # Gemini API often prefers history to start with user.
        
        # We will prepend system instruction to the LATEST message for the single-turn RAG effect, 
        # but to keep conversation flow we can rely on history.
        # However, for strong adhering to context, repeating context in the latest prompt is effective.
        
        for msg in request.history:
            role = "user" if msg.role == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg.content]})
            
        # 5. Start Chat Session
        chat = model.start_chat(history=gemini_history)
        
        # 6. Send Message with Context
        # We attach the system prompt to the user's current message to ensure it's in focus
        full_prompt = f"{system_instruction}\n\nUser Question: {request.message}"
        
        response = chat.send_message(full_prompt)
        
        return ChatResponse(reply=response.text)
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        # Fallback Logic
        print("Falling back to rule-based bot due to AI error.")
        
        reply_text = ""
        msg_lower = request.message.lower()
        
        # 1. Job Search Intent
        if any(w in msg_lower for w in ["job", "find", "looking for", "career", "work", "hiring"]):
            # Extract role from profile or message
            role_to_search = ""
            if current_user and current_user.job_preferences:
                role_to_search = current_user.job_preferences[0]
            
            # Try to find role in message
            for role in SKILL_KNOWLEDGE_BASE.keys():
                if role.lower() in msg_lower:
                    role_to_search = role
                    break
            
            if role_to_search:
                reply_text += f"I can help you find <b>{role_to_search}</b> jobs. Since I'm having trouble connecting to my main AI brain, I'll do a quick search provided by the platform.\n\n"
                # Mock search result text
                reply_text += f"Here are some top skills you might need for {role_to_search}: {', '.join(SKILL_KNOWLEDGE_BASE.get(role_to_search, []))}.\n\n"
                reply_text += "You can use the main <b>Search</b> page to find live listings."
            else:
                reply_text += "I can help you find jobs. What role are you looking for? (e.g. Frontend Developer, Data Scientist)"
                
        # 2. Resume & Cover Letter Intent
        elif any(w in msg_lower for w in ["resume", "cv", "improve", "review", "cover letter"]):
            if "cover letter" in msg_lower:
                # Simple Template Generator
                role = "Software Engineer"
                company = "Tech Corp"
                # improving extraction logic slightly
                words = msg_lower.split()
                if "for" in words:
                    try:
                        role_idx = words.index("for") + 1
                        role = words[role_idx].capitalize()
                    except: pass
                
                reply_text += f"Here is a draft cover letter for a <b>{role}</b> position:\n\n"
                reply_text += f"Dear Hiring Manager,\n\nI am writing to express my strong interest in the {role} position at {company}. With my background in [Your Skills], I am confident in my ability to contribute effectively to your team.\n\n"
                reply_text += "In my previous role, I [mention a key achievement]. I am particularly drawn to this opportunity because [mention why].\n\nThank you for considering my application.\n\nSincerely,\n[Your Name]"
            
            elif current_user and current_user.skills:
                reply_text += "To improve your resume, make sure to highlight your key skills: " + ", ".join(current_user.skills[:5]) + ".\n\n"
                reply_text += "Quantify your achievements in your experience section (e.g., 'Improved performance by 20%')."
            else:
                 reply_text += "I can help improve your resume. Upload your resume in the 'Resume Builder' section or update your profile skills first."

        # 3. Mock Interview Intent
        elif any(w in msg_lower for w in ["interview", "quiz", "question"]):
            topic = "General"
            if "react" in msg_lower: topic = "React"
            elif "python" in msg_lower: topic = "Python"
            elif "node" in msg_lower: topic = "Node.js"
            elif "sql" in msg_lower: topic = "SQL"
            
            questions = {
                "React": "What is the Virtual DOM and how does it improve performance?",
                "Python": "Explain the difference between a list and a tuple.",
                "Node.js": "What is the Event Loop in Node.js?",
                "SQL": "What is the difference between INNER JOIN and LEFT JOIN?",
                "General": "Tell me about a challenging project you worked on and how you overcame obstacles."
            }
            
            q = questions.get(topic, questions["General"])
            reply_text += f"Sure, let's do a mock interview for <b>{topic}</b>.\n\nHere is your question:\n\n<b>{q}</b>\n\n(Type your answer and I'll evaluate it!)"

        # 4. Profile/Skills Intent
        elif any(w in msg_lower for w in ["skill", "learn", "study"]):
             reply_text += "Based on market trends, I recommend mastering: "
             rec_skills = []
             if current_user and current_user.job_preferences:
                 for pref in current_user.job_preferences:
                    for role, skills in SKILL_KNOWLEDGE_BASE.items():
                         if role in pref:
                             rec_skills.extend(skills)
             
             if rec_skills:
                 reply_text += ", ".join(list(set(rec_skills))[:5])
             else:
                 reply_text += "React, Python, Cloud Computing, and System Design."
                 
        # 4. Greeting/General
        elif any(w in msg_lower for w in ["hi", "hello", "hey", "help"]):
            reply_text += "Hello! I am JobBot. I can help you find jobs, improve your resume, or suggest new skills. What would you like to do?"
            
        else:
            reply_text += "I am currently running in <b>Offline Mode</b> (Basic). I can still help you with basic job tips and navigation. Ask me about jobs, resumes, or skills!"
            
        return ChatResponse(reply=reply_text)
