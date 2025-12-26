from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Job Schemas
class Job(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: str
    description: Optional[str] = None
    url: str
    source: str
    posted_date: Optional[str] = None
    salary: Optional[str] = None

class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    limit: int = 10
    start: int = 1
    experience_level: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    company_size: Optional[List[str]] = None  # Added company size filter

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserLogin(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    total_experience: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    avatar: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    education: Optional[List[dict]] = None
    experience: Optional[List[dict]] = None
    job_preferences: Optional[List[str]] = None
    projects: Optional[List[dict]] = None

class UserResponse(UserBase):
    id: int
    full_name: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    total_experience: Optional[str] = None
    skills: Optional[List[str]] = []
    preferred_locations: Optional[List[str]] = []
    avatar: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    education: Optional[List[dict]] = []
    experience: Optional[List[dict]] = []
    job_preferences: Optional[List[str]] = []
    projects: Optional[List[dict]] = []
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Application Schemas
class ApplicationBase(BaseModel):
    job_title: str
    company: str
    location: Optional[str] = None
    status: Optional[str] = "Saved"
    notes: Optional[str] = None
    salary: Optional[str] = None
    job_url: Optional[str] = None
    platform: Optional[str] = None
    job_id: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    applied_date: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

