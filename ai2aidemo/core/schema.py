from pydantic import BaseModel, Field
from typing import Union, Dict, List, Any, Optional

class Education(BaseModel):
    degree: str = Field(default="Not specified")
    major: str = Field(default="Not specified")
    university: str = Field(default="Not specified")

class ResumeBase(BaseModel):
    """Legacy support - will be deprecated"""
    name: str
    education: Education
    experience: str
    skills: List[str]
    projects: List[str] = Field(default_factory=list)
    others: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True

class CharacterProfile(BaseModel):
    """Base model for character profile in discussions"""
    name: str
    background: str  # General background/context
    interests: List[str] = Field(default_factory=list)  # Topics of interest
    knowledge_areas: List[str] = Field(default_factory=list)  # Areas of knowledge
    personality: Optional[str] = None

class RolePlayInput(BaseModel):
    """Input model for text-based character creation"""
    name: str
    description: str  # Free-form description of the character
    personality: Optional[str] = None 