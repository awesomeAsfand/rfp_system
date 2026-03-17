from ninja import Router, File, Form
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from .models import RFPDocument, Requirement
from .tasks import process_rfp_document
from .schemas import RFPUploadOut, RFPDetailOut, RequirementOut
from knowledge.models import Tenant
from knowledge.auth import TenantAPIKey

auth= TenantAPIKey()
router = Router(auth=auth)

@router.post("/upload", response=RFPUploadOut)
def upload_rfp(request, title:Form[str], client_name:Form[str],file:File[UploadedFile]):
    tenant = request.auth
    allowed = ['.pdf', '.docx', '.doc']
    extension = '.' + file.name.split('.')[-1].lower()
    if extension not in allowed:
        return router.create_response(
            request, {"detail":"Only PDF and DOCX files are supported"}, status=400
        )
    
    rfp = RFPDocument.objects.create(
        tenant=tenant,
        title=title,
        client_name=client_name,
        file=file,
    )
    process_rfp_document.delay(str(rfp.id))
    return rfp


@router.get("", response=list[RFPUploadOut])
def list_rfp(request):
    tenant = request.auth
    return RFPDocument.objects.filter(tenant=tenant).order_by("-uploaded_at")

@router.get("/{rfp_id}", response=RFPDetailOut)
def get_rfp(request, rfp_id:str):
    tenant= request.auth
    rfp = get_object_or_404(RFPDocument, id=rfp_id, tenant=tenant)
    return rfp

@router.get("/{rfp_id}/requirements", response=list[RequirementOut])
def list_requirements(request, rfp_id:str, requirement_type:str=None, priority:str=None, status:str=None):
    tenant= request.auth
    rfp = get_object_or_404(RFPDocument, id=rfp_id, tenant=tenant)
    qs = Requirement.objects.filter(rfp=rfp)
    
    if requirement_type:
        qs = qs.filter(requirement_type=requirement_type)
    if priority:
        qs = qs.filter(priority=priority)
    if status:
        qs = qs.filter(status=status)

    return qs

@router.get("/{rfp_id}/summary")
def get_rfp_summary(request, rfp_id:str):
    tenant = request.auth
    rfp = get_object_or_404(RFPDocument, id=rfp_id, tenant=tenant)
    requirements = Requirement.objects.get(rfp=rfp)
    
    for req in requirements:
        by_type[req.requirement_type] = by_type.get(req.requirement_type, 0) + 1
        by_priority[req.priority] = by_priority.get(req.priority, 0) + 1
        by_status[req.status] = by_status.get(req.status, 0) + 1

    return {
        "rfp_id": str(rfp.id),
        "title": rfp.title,
        "total_requirements": requirements.count(),
        "by_type": by_type,
        "by_priority": by_priority,
        "by_status": by_status,
    }
