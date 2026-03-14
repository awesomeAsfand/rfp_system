from celery import shared_task
from django.utils import timezone
import logging
from .models import KnowledgeAsset
from .services import DocumentProcessor



logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_knowledge_asset(self, asset_id:str):
    try:
        asset = KnowledgeAsset.objects.get(id=asset_id)
        asset.status = KnowledgeAsset.Status.PROCESSING
        asset.save()

        processor = DocumentProcessor(asset)
        chunk_count = processor.porcess()

        asset.status = KnowledgeAsset.Status.READY
        asset.chunk_count = chunk_count
        asset.processed_at = timezone.now()
        asset.save()

        logger.info(f"Asset {asset.id} process: {chunk_count} chunks created")
        return chunk_count
    except KnowledgeAsset.DoesNotExist:
        logger.error(f"Asset {asset_id} not found")
    except Exception as exc:
        logger.error(f"failed to process asses{asset.id}:{exc}")
    
    try:
        raise self.retry(exc=exc, countdown=60*(2 ** self.max_retries))
    except self.MaxRetriesExceededError:
        asset = KnowledgeAsset.objects.get(id=asset_id)
        asset.status = KnowledgeAsset.Status.FAILED
        asset.error_message = str(exc)
        asset.save()
