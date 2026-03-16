from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from .extraction_schemas import ExtractionResult
import os
import logging

logger = logging.getLogger(__name__)

MAX_CHAR_PER_PASS = 80000


def __init__(self, rfp_document):
    rfp_document = self.rfp_document
    self.llm = ChatOpenAI(
        model = "openai/o4-mini",
        temperature=0,
        openai_api_key=settings.GITHUB_TOKEN
    )

    self.structured_llm = self.llm.with_structured_output(ExtractionResult)

def process(self) -> int:
    raw_text = self._load_document()
    logger.info(f"Loaded RFP: {len(raw_text)} characters")

    all_requirements= []
    if len(raw_text) < MAX_CHAR_PER_PASS:
        result = self._extract_requirements(raw_text)
        all_requirements = result.requirements
    else:
        all_requirements = self._extract_large_document(raw_text)
    
    self._save_requirements(all_requirements)
    return len(all_requirements)

def _load_document(self)->str:
    file_path = self.rfp.file.path
    extension = os.path.splitdrive(file_path)[-1].lower()
    if extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif extension in ['.docx', 'doc']:
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"file type unsupported {extension}")
    documents = loader.load()
    full_text = ""
    #Combine all pages into one string with page markers
    # The page markers help the LLM identify section references
    for i, doc in enumerate(documents):
        full_text += f"\n\n--- PAGE {i + 1} ---\n\n"
        full_text += doc.page_content

    return full_text

def _extract_requirements(self, text:str) -> ExtractionResult:

    prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing RFP (Request for Proposal) 
            documents and extracting structured requirements.
            Your job is to identify every distinct requirement in the document.

            A requirement is any statement that:
            - Describes something the vendor MUST, SHOULD, or MAY provide
            - Specifies a technical capability, feature, or standard
            - Describes a commercial term, SLA, or delivery expectation  
            - States a legal, compliance, or regulatory obligation

            DO NOT extract:
            - Background or context paragraphs
            - Definitions of terms
            - Instructions about how to submit the proposal
            - General descriptions of the client's organization

            Be thorough. A typical RFP has between 15 and 80 requirements.
            Extract ALL of them, even if they seem minor."""),
            ("human", """Please extract all requirements from the following RFP document.
            RFP DOCUMENT:
            {document_text} Extract every requirement and return them as structured data.""")
            ])

    chain = prompt | self.structured_llm
    result = chain.invoke({"document_text":text})
    logger.info(f"extracted {result.total_count}")
    return result




def _extract_large_document(self, text:str) -> list:
    sections = []
    overlap = 2000
    start = 0
    while start < len(text):
        end = start + MAX_CHAR_PER_PASS
        sections.append(text[start:end])
        start = end - overlap
    logger.info(f"larger documnet processing in{len(sections)} sections")
    #This part of the function processes each text section, extracts requirements from it, 
    # and combines them into one final list while keeping positions unique.
    

    


def _save_requirements(self, requirements: list):
    pass