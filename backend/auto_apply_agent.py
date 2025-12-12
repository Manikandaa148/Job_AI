"""
Auto-Apply AI Agent
Handles automatic job applications based on user preferences and profile data.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class AutoApplyAgent:
    """AI Agent that manages automatic job applications"""
    
    # Required fields for job applications
    REQUIRED_FIELDS = {
        "basic_info": ["full_name", "email", "location"],
        "professional": ["experience_level", "skills"],
        "contact": [],  # Optional but recommended
        "documents": []  # Will check for resume/cover letter if needed
    }
    
    def __init__(self, user_data: Dict):
        """Initialize the agent with user data"""
        self.user_data = user_data
        self.missing_fields = []
        self.application_status = []
        
    def validate_profile_completeness(self) -> Tuple[bool, List[str]]:
        """
        Validate if user profile has all required information for auto-apply.
        Returns: (is_complete, missing_fields)
        """
        missing = []
        
        # Check basic info
        for field in self.REQUIRED_FIELDS["basic_info"]:
            if not self.user_data.get(field):
                missing.append(field)
        
        # Check professional info
        for field in self.REQUIRED_FIELDS["professional"]:
            value = self.user_data.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                missing.append(field)
        
        # Check if user has at least one education entry
        education = self.user_data.get("education", [])
        if not education or len(education) == 0:
            missing.append("education")
        
        # Check if user has at least one experience entry
        experience = self.user_data.get("experience", [])
        if not experience or len(experience) == 0:
            missing.append("experience")
        
        # Check job preferences
        job_preferences = self.user_data.get("job_preferences", [])
        if not job_preferences or len(job_preferences) == 0:
            missing.append("job_preferences")
        
        self.missing_fields = missing
        return len(missing) == 0, missing
    
    def get_missing_field_prompts(self) -> List[Dict[str, str]]:
        """
        Generate chatbot prompts for missing fields.
        Returns list of prompts with field name and user-friendly question.
        """
        prompts = []
        
        field_questions = {
            "full_name": "What's your full name?",
            "email": "What's your email address?",
            "location": "Where are you located? (City, State/Country)",
            "experience_level": "What's your experience level? (Entry Level, Mid Level, Senior, Lead, etc.)",
            "skills": "What are your key skills? (Please list them separated by commas)",
            "education": "Could you share your education details? (Degree, Institution, Year)",
            "experience": "Tell me about your work experience (Company, Role, Duration)",
            "job_preferences": "What types of jobs are you looking for? (e.g., Full-time, Remote, etc.)"
        }
        
        for field in self.missing_fields:
            if field in field_questions:
                prompts.append({
                    "field": field,
                    "question": field_questions[field],
                    "type": self._get_field_type(field)
                })
        
        return prompts
    
    def _get_field_type(self, field: str) -> str:
        """Determine the input type for a field"""
        if field in ["skills", "job_preferences"]:
            return "list"
        elif field in ["education", "experience", "projects"]:
            return "structured"
        else:
            return "text"
    
    def can_auto_apply(self) -> bool:
        """Check if auto-apply is possible"""
        is_complete, _ = self.validate_profile_completeness()
        return is_complete
    
    def prepare_application_data(self, job: Dict) -> Dict:
        """
        Prepare application data for a specific job.
        This would be used to fill out application forms.
        """
        return {
            "personal_info": {
                "name": self.user_data.get("full_name", ""),
                "email": self.user_data.get("email", ""),
                "phone": self.user_data.get("phone", ""),
                "address": self.user_data.get("address", ""),
                "location": self.user_data.get("location", "")
            },
            "professional_info": {
                "experience_level": self.user_data.get("experience_level", ""),
                "skills": self.user_data.get("skills", []),
                "linkedin": self.user_data.get("linkedin_url", ""),
                "github": self.user_data.get("github_url", ""),
                "portfolio": self.user_data.get("portfolio_url", "")
            },
            "education": self.user_data.get("education", []),
            "experience": self.user_data.get("experience", []),
            "projects": self.user_data.get("projects", []),
            "job_preferences": self.user_data.get("job_preferences", []),
            "job_details": {
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "url": job.get("url", "")
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_application(self, job: Dict) -> Dict:
        """
        Simulate job application process.
        In production, this would integrate with actual job platforms.
        """
        application_data = self.prepare_application_data(job)
        
        # Simulate application result
        result = {
            "success": True,
            "job_id": job.get("id", ""),
            "job_title": job.get("title", ""),
            "company": job.get("company", ""),
            "applied_at": datetime.now().isoformat(),
            "status": "submitted",
            "message": f"Successfully applied to {job.get('title')} at {job.get('company')}"
        }
        
        self.application_status.append(result)
        return result
    
    def get_application_summary(self) -> Dict:
        """Get summary of all applications"""
        return {
            "total_applications": len(self.application_status),
            "successful": len([a for a in self.application_status if a["success"]]),
            "failed": len([a for a in self.application_status if not a["success"]]),
            "applications": self.application_status
        }


def validate_user_for_auto_apply(user_data: Dict) -> Dict:
    """
    Validate user data for auto-apply feature.
    Returns validation result with missing fields if any.
    """
    agent = AutoApplyAgent(user_data)
    is_complete, missing_fields = agent.validate_profile_completeness()
    
    return {
        "can_auto_apply": is_complete,
        "missing_fields": missing_fields,
        "prompts": agent.get_missing_field_prompts() if not is_complete else []
    }


def process_auto_apply(user_data: Dict, jobs: List[Dict]) -> Dict:
    """
    Process auto-apply for multiple jobs.
    Returns application results.
    """
    agent = AutoApplyAgent(user_data)
    
    # Validate first
    if not agent.can_auto_apply():
        is_complete, missing = agent.validate_profile_completeness()
        return {
            "success": False,
            "error": "Profile incomplete",
            "missing_fields": missing,
            "prompts": agent.get_missing_field_prompts()
        }
    
    # Apply to jobs
    results = []
    for job in jobs:
        result = agent.simulate_application(job)
        results.append(result)
    
    return {
        "success": True,
        "summary": agent.get_application_summary(),
        "results": results
    }
