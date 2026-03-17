from ninja import Schema
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class RFPUploadOut(Schema):

    id:UUID
    title:str
    client_name:str
    status:str
    requirement_count:int
    uploaded_at:datetime

    class Config:
        from_attributes:True

class RequirementOut(Schema):

    id:UUID
    section_reference:str
    requirement_text:str
    requirement_type:str
    priority:str
    status:str
    draft_response:str
    reviewer_notes:str
    position:int

    class Config:
        from_attributes:True

class RFPDetailOut(Schema):

    id:UUID
    title:str
    client_name:str
    status:str
    requirement_count:int
    uploaded_at:datetime
    processed_at:Optional[datetime]
    requirements:List[RequirementOut]

    class Config:
        from_attributes = True

class RequirementFilterIn(Schema):

    requirement_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None