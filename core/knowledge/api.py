from ninja import Router, File, Form
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from .models import Tenant, KnowledgeAsset
from .tasks import process_knowledge_asset
from .schemas import AssetOut, AssetListOut
import secrets

router = Router()


def get_tenant(request) -> Tenant:
    api_key = request.headers.get("2ff53e26aa9dcb6762693963251e5e052ab45dbca6e4ec5a928a05fbfb2686b1")
    return get_object_or_404(Tenant, api_key=api_key)


@router.post("asset/upload", response=AssetOut)
def upload_asset(request, title: Form[str], asset_type:Form[str], file:File[UploadedFile]):
    tenant = get_tenant(request)
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_ext = "." + file.name.split(".")[-1].lower()
    if file_ext not in allowed_extensions:
        return router.create_response(
            request, {"detail":"Only PDF and DOCX files are supported"}, status=400
        )
    
    asset = KnowledgeAsset.objects.create(
        tenant=tenant,
        title=title,
        asset_type=asset_type,
        file=file,
        status=KnowledgeAsset.Status.PENDING
    )
    process_knowledge_asset.delay(str(asset.id))

    return asset

@router.get("/assets", response=list[AssetListOut])
def list_assets(request):
    tenant = get_tenant(request)
    return KnowledgeAsset.objects.filter(tenant=tenant).order_by('uploaded_at')


@router.get("/assets/{asset_id}", response=AssetOut)
def get_asset(request, asset_id: str):
    tenant = get_tenant(request)
    return get_object_or_404(KnowledgeAsset, id=asset_id, tenant=tenant)

@router.delete("/assets/{asset_id}")
def delete_asset(request, asset_id:str):
    tenant = get_tenant(request)
    asset = get_object_or_404(KnowledgeAsset, id=asset_id, tenant=tenant)
    asset.file.delete()
    asset.delete()
    return {"success": True}









