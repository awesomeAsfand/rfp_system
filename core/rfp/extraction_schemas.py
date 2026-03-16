from pydantic import BaseModel, Field
from typing import List
from enum import Enum


"""This is the blueprint of what you want the AI to return. 
LangChain will use this schema to force the LLM to output structured, 
validated data — not free-form text."""



class RequirementTypeEnum(str, Enum):
    technical = "technical"
    commercial = "commercial"
    legal = "legal"
    operational = "operational"
    administrative = "administrative"
    other = "other"

class PriorityEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


"""
Represents a single requirement extracted from an RFP.

Every field has a description — this description is actually
read by the LLM to understand what you want. Be precise here.
Vague"""

class ExtractedRequirement(BaseModel):

    section_reference : str = Field(
        description="The section number or reference where this requirement appears, e.g. '3.2.1' or 'Section 4'. Empty string if not identifiable."
    )
    requirement_text:str = Field(
        description="The complete, verbatim text of the requirement as it appears in the document. Do not paraphrase."
    )
    requirement_type: RequirementTypeEnum = Field(
        description=(
            "Classify the requirement: "
            "technical=technology/system/integration requirements, "
            "commercial=pricing/payment/contract terms, "
            "legal=compliance/regulatory/legal obligations, "
            "operational=delivery/SLA/support requirements, "
            "administrative=reporting/documentation requirements, "
            "other=anything that doesn't fit the above"
        )

    )
    priority: PriorityEnum = Field(
        description=(
            "Assess priority based on language used: "
            "high=mandatory/must/shall/required, "
            "medium=should/expected/preferred, "
            "low=may/optional/nice to have"
        )
    )

    position: int = Field(
        description="The sequential position of this requirement in the document, starting from 1."
    )

class ExtractionResult(BaseModel):
    requirements : List[ExtractedRequirement] = Field(
        description="All requirements extracted from the RFP document."
    )

    total_count: int = Field(
        description="Total number of requirements extracted."
    )

    document_summary: str = Field(
        description="A 2-3 sentence summary of what this RFP is asking for overall."
    )











