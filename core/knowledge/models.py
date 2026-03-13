import uuid
from django.db import models
from pgvector.django import VectorField

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Is it "HAS-A"? → use composition (class inside class) knowledgebase HAS-A Asset or Status

class KnowledgeAsset(models.Model):
    class AssetType(models.TextChoices):
        PROPOSAL = 'proposal', 'Past Proposal'
        CASE_STUDY = 'case_study', 'Case Study'
        TEAM_BIO = 'team_bio', 'Team Bio'
        CERTIFICATION = 'certification', 'Certification'
        COMPANY_INFO = 'company_info', 'Company Information'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'        # Just uploaded, not processed yet
        PROCESSING = 'processing', 'Processing'  # Celery task is running
        READY = 'ready', 'Ready'              # Fully processed, searchable
        FAILED = 'failed', 'Failed'           # Something went wrong

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="assets")
    title = models.CharField(max_length=500)
    asset_type = models.CharField(
        max_length=50,
        choices=AssetType.choices,
        default=AssetType.OTHER   
    )
    file = models.FileField(upload_to='knowledge_assets/%Y/%m/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    error_message = models.TextField(blank=True)  # Store what went wrong if failed
    chunk_count = models.IntegerField(default=0)  # How many chunks were created
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.title}"

class AssetChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(KnowledgeAsset, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    chunk_index = models.IntegerField()
    metadata = models.JSONField(default=dict)

class Meta:
    ordering = ['asset', 'chunk_index']

def __str__(self):
    return f"Chunk {self.chunk_index} of {self.asset.title}"









    

    

    



