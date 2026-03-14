from ninja.security import APIKeyHeader
from ninja import errors
from .models import Tenant

class TenantAPIKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        try:
            return Tenant.objects.get(api_key=key)
        except Tenant.DoesNotExist:
            return None

            
