from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum
from database import Base
import json
import enum
from datetime import datetime

class ApplicationStatus(str, enum.Enum):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(String, nullable=True)  # External ID from scraper
    job_title = Column(String)
    company = Column(String)
    location = Column(String, nullable=True)
    status = Column(String, default=ApplicationStatus.SAVED.value) 
    applied_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    salary = Column(String, nullable=True)
    job_url = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    _skills = Column("skills", Text, nullable=True, default="[]") # Store as JSON string

    @property
    def skills(self):
        if self._skills and self._skills != "[]":
            try:
                return json.loads(self._skills)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @skills.setter
    def skills(self, value):
        if value is None:
            self._skills = "[]"
        else:
            self._skills = json.dumps(value) if isinstance(value, list) else "[]"

    _education = Column("education", Text, nullable=True, default="[]")
    _experience = Column("experience", Text, nullable=True, default="[]")
    _job_preferences = Column("job_preferences", Text, nullable=True, default="[]")
    _projects = Column("projects", Text, nullable=True, default="[]")

    @property
    def education(self):
        if self._education and self._education != "[]":
            try:
                return json.loads(self._education)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @education.setter
    def education(self, value):
        if value is None:
            self._education = "[]"
        else:
            self._education = json.dumps(value) if isinstance(value, list) else "[]"

    @property
    def experience(self):
        if self._experience and self._experience != "[]":
            try:
                return json.loads(self._experience)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @experience.setter
    def experience(self, value):
        if value is None:
            self._experience = "[]"
        else:
            self._experience = json.dumps(value) if isinstance(value, list) else "[]"

    @property
    def job_preferences(self):
        if self._job_preferences and self._job_preferences != "[]":
            try:
                return json.loads(self._job_preferences)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @job_preferences.setter
    def job_preferences(self, value):
        if value is None:
            self._job_preferences = "[]"
        else:
            self._job_preferences = json.dumps(value) if isinstance(value, list) else "[]"

    @property
    def projects(self):
        if self._projects and self._projects != "[]":
            try:
                return json.loads(self._projects)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @projects.setter
    def projects(self, value):
        if value is None:
            self._projects = "[]"
        else:
            self._projects = json.dumps(value) if isinstance(value, list) else "[]"

    total_experience = Column(String, nullable=True)
    
    _preferred_locations = Column("preferred_locations", Text, nullable=True, default="[]")

    @property
    def preferred_locations(self):
        if self._preferred_locations and self._preferred_locations != "[]":
            try:
                return json.loads(self._preferred_locations)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @preferred_locations.setter
    def preferred_locations(self, value):
        if value is None:
            self._preferred_locations = "[]"
        else:
            self._preferred_locations = json.dumps(value) if isinstance(value, list) else "[]"

    resume_score = Column(Integer, nullable=True)
    resume_path = Column(String, nullable=True)
