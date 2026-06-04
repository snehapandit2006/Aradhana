from pydantic import BaseModel, Field, validator
from typing import Optional
import re
from datetime import datetime

class BirthData(BaseModel):
    name: str = Field(..., description="Full name of the user")
    date: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    time: Optional[str] = Field(None, description="Time of birth in HH:MM format (24-hour clock)")
    time_unknown: bool = Field(False, description="Flag indicating if the birth time is unknown")
    place: str = Field(..., description="Place/City of birth")

    @validator('date')
    def validate_date(cls, v):
        try:
            birth_date = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        if birth_date > datetime.now().date():
            raise ValueError("Birth date cannot be in the future")
        return v

    @validator('time')
    def validate_time(cls, v, values):
        if values.get('time_unknown'):
            return None
        if not v:
            return None
        if not re.match(r'^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError("Time must be in HH:MM (24-hour) format")
        return v

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier (UUID)")
    message: str = Field(..., description="User message")
    birth_data: Optional[BirthData] = Field(None, description="User's birth details, if being submitted or updated")

    @validator('session_id')
    def validate_session_id(cls, v):
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v.lower()):
            raise ValueError("Session ID must be a valid UUID")
        return v.lower()
