from django.conf import settings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import tempfile
import os
import logging
from .models import AssetChunk


logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles the full pipeline for a single KnowledgeAsset:
    1. Load the file (PDF or DOCX)
    2. Split it into chunks
    3. Embed each chunk with OpenAI
    4. Save chunks + embeddings to the database
    """
    def __init__(self, asset):
        self.asset = asset
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.GITHUB_TOKEN,
            openai_api_base=settings.GITHUB_MODELS_BASE_URL,
            model="text-embedding-ada-002"
        )

        # How to split documents into chunks
        # chunk_size: max characters per chunk
        # chunk_overlap: how many characters overlap between chunks
        #   (overlap is important — it prevents cutting a sentence in half
        #    and losing context at the boundary between chunks)

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process(self) -> int:
        documents= self._load_document() # Step 1: Load the raw text from the file
        chunks = self.splitter.split_documents(documents)# Step 2: Split into chunks
        logger.info(f"split into {len(chunks)} chunks")
        texts = [chunk.page_content for chunk in chunks]# Step 3: Embed all chunks in one API call (batching is efficient)
        embeddings = self.embeddings.embed_documents(texts)# embeddings is now a list of 1536-dim vectors, one per chunk
        self._save_chunks(chunks, embeddings)
        return len(chunks)



    def _load_document(self):
        file_path = self.asset.file.path
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".pdf":
            loader = PyPDFLoader(file_path)
        elif extension in [".docx", ".doc"]:
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type:{extension}")

        documents = loader.load()
        logger.info(f"loaded {len(documents)} pages from {self.asset.title}")
        return documents

    def _save_chunks(self, chunks, embeddings):
        AssetChunk.objects.filter(asset=self.asset).delete()
        
        asset_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            asset_chunks.append(
                AssetChunk(
                    asset=self.asset,
                    content=chunk.page_content,
                    embedding=embeddings,
                    chunk_index=i,
                    metadata={
                        'page': chunk.metadata.get('page',0),
                        'source': chunk.metadata.get('source',''),
                        'asset_type': self.asset.asset_type,
                    }

                )
            )
        AssetChunk.objects.bulk_create(asset_chunks)
        logger.info(f"saved {len(asset_chunks)} chunks into database")