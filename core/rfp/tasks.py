from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_rfp_document(self, rfp_id:str):
    from .models import RFPDocument
    from .services import RFPProcessor
    try:
        rfp = RFPDocument.objects.get(id=rfp_id)
        rfp.status = RFPDocument.Status.PROCESSING
        rfp.save()

        processor = RFPProcessor(rfp)
        count = processor.process()
        rfp.status = RFPDocument.Status.EXTRACTED
        rfp.requirement_count=count
        rfp.processed_at = timezone.now()
        rfp.save()
        logger.info(f"RFP {rfp_id}: {count} requirements extracted")
        return count
    except RFPDocument.DoesNotExist:
        logger.info(f"RFP {rfp_id} not found")
        raise
    
    except Exception as exc:
        logger.error(f"RFP {rfp_id} processing failed: {exc}")
        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            rfp = RFPDocument.objects.get(id=rfp_id)
            rfp.status = RFPDocument.Status.FAILED
            rfp.error_message = str(exc)
            rfp.save()







