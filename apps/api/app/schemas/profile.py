from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class Link(BaseModel):
    type: str
    url: Optional[str] = None
    label: Optional[str] = None


class WorkExperience(BaseModel):
    company: str
    title: str
    startDate: str
    endDate: Optional[str] = None
    location: Optional[str] = None
    employmentType: Optional[str] = None  # full-time, part-time, contract, freelance, internship
    description: Optional[str] = None  # Overall job description/summary
    technologies: List[str] = []  # Tech stack/tools used
    achievements: List[str] = []  # Key achievements/accomplishments
    bullets: List[str] = []  # Detailed responsibilities


class Education(BaseModel):
    school: str
    degree: str
    field: Optional[str] = None  # Field of study/major
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    gpa: Optional[float] = None
    grade: Optional[str] = None  # Alternative to GPA (e.g., "First Class", "Distinction")
    honors: Optional[List[str]] = None  # Honors, awards, distinctions
    relevantCoursework: Optional[List[str]] = None  # Relevant courses taken
    activities: Optional[List[str]] = None  # Clubs, organizations, extracurriculars
    thesis: Optional[str] = None  # Thesis/project title if applicable
    bullets: Optional[List[str]] = None


class Project(BaseModel):
    name: str
    link: Optional[str] = None
    description: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    role: Optional[str] = None  # Your role in the project
    teamSize: Optional[int] = None
    status: Optional[str] = None  # completed, in-progress, on-hold
    outcomes: Optional[List[str]] = None  # Results/impact of the project
    tech: List[str] = []
    bullets: List[str] = []


class Skill(BaseModel):
    name: str
    category: Optional[str] = None  # Programming, Tools, Soft Skills, etc.
    level: Optional[str] = None  # beginner, intermediate, advanced, expert
    yearsExperience: Optional[float] = None  # Years of experience with this skill


class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    expiryDate: Optional[str] = None
    credentialId: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None  # What the certification covers
    skills: Optional[List[str]] = None  # Skills gained from this certification
    verification: Optional[str] = None  # How to verify this certification


class Award(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None  # Academic, Professional, Leadership, etc.
    description: Optional[str] = None
    recognition: Optional[str] = None  # What was recognized


class Language(BaseModel):
    name: str
    proficiency: Optional[str] = None  # native, fluent, conversational, basic
    reading: Optional[str] = None
    writing: Optional[str] = None
    speaking: Optional[str] = None


class Preferences(BaseModel):
    visaStatus: Optional[str] = None
    workAuth: Optional[str] = None
    relocation: Optional[bool] = None
    remote: Optional[bool] = None
    salary: Optional[str] = None  # Expected salary range
    availability: Optional[str] = None  # Notice period, available from date


class Basics(BaseModel):
    firstName: str
    lastName: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None  # Professional summary/objective
    languages: Optional[List[str]] = None  # Languages spoken
    links: List[Link] = []


class ProfileSchema(BaseModel):
    basics: Basics
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    projects: List[Project] = []
    skills: List[Skill] = []
    languages: Optional[List[Language]] = None
    certifications: Optional[List[Certification]] = None
    awards: Optional[List[Award]] = None
    preferences: Optional[Preferences] = None


class ProfileCreate(BaseModel):
    profile: ProfileSchema


class ProfileUpdate(BaseModel):
    profile: ProfileSchema


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    profile: ProfileSchema
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileCompleteness(BaseModel):
    education: bool = False
    experience: bool = False
    skills: bool = False
    projects: bool = False
    publications: bool = False


class ProfileStatus(BaseModel):
    hasProfile: bool = False
    profileId: Optional[str] = None
    profileCompleteness: ProfileCompleteness = ProfileCompleteness()
    profile: Optional[ProfileSchema] = None
