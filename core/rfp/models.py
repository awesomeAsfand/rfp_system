from django.db import models
from knowledge.models import Tenant
import uuid

class RFPDocument(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        EXTRACTED = 'extracted', 'Requirements Extracted'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="rfp_documents")
    title = models.CharField(max_length=500)
    client_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='rfp_documents/%Y/%m/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    requirement_count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.client_name} — {self.title}"

class Requirement(models.Model):
    class Priority(models.TextChoices):
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Draft'
        DRAFT = 'draft', 'Draft Generated'
        IN_REVIEW = 'in_review', 'In Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    class RequirementType(models.TextChoices):
        TECHNICAL = 'technical', 'Technical'
        COMMERCIAL = 'commercial', 'Commercial'
        LEGAL = 'legal', 'Legal'
        OPERATIONAL = 'operational', 'Operational'
        ADMINISTRATIVE = 'administrative', 'Administrative'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rfp = models.ForeignKey(RFPDocument, on_delete=models.CASCADE, related_name="requirements")
    section_reference = models.CharField(max_length=50, blank=True)
    requirement_text = models.TextField()
    requirement_type = models.CharField(max_length=30, choices=RequirementType.choices, default=RequirementType.OTHER)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)


    # These fields are populated in Phase 3 (draft generation)
    draft_response = models.TextField(blank=True)
    reviewer_notes = models.TextField(blank=True)

    extracted_at = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(default=0)  # Order in the original document

    
    def __str__(self):
        return f"Requirement from {self.rfp.title}"
