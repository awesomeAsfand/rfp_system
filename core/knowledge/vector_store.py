from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from .models import AssetChunk
import logging


logger = logging.getLogger(__name__)

"""
    A wrapper around pgvector similarity search on our AssetChunk table.

    Why not use LangChain's built-in PGVector store?
    Because LangChain's PGVector manages its own table with its own schema.
    We need to search OUR table so we can enforce tenant isolation —
    a company must never see another company's content.

    This class does one thing: given a text query and a tenant,
    return the most relevant chunks from that tenant's knowledge base.
    """

class KnowledgeBaseSearch:
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.GITHUB_TOKEN,
            openai_api_base=settings.GITHUB_MODELS_BASE_URL,
            model="text-embedding-3-small"
        )
    
    def search(self, query:str, k:int=5, asset_type:str=None)->list[Document]:
        
        #query:The text to search for (e.g. the requirement text)
        # Step 1: Embed the query text into a vector
        # This is the same operation done to each chunk during Phase 1 ingestion
        query_vector = self.embeddings.aembed_query(query)
        chunks = AssetChunk.objects.filter(asset__tenant=self.tenant, asset__status="ready")
        if asset_type:
            chunks = chunks.filter(metadata__asset_type=asset_type)

        from pgvector.django import L2Distance
        chunks = chunks.order_by(
            L2Distance('embeddiing', query_vector)
        )[:5]

        documents = []
        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk.content,
                    metadata={
                        'asset_id': str(chunk.asset.id),
                        'asset_title': chunk.asset.title,
                        'asset_type': chunk.asset.asset_type,
                        'chunk_index': chunk.chunk_index,
                        'page': chunk.metadata.get('page', 0),
                    }
                )
            )
        
            logger.info(
                f"Vector search for tenant {self.tenant.name}: "
                f"found {len(documents)} chunks for query '{query[:50]}...'")
        return documents














