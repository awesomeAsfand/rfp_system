from ninja import NinjaAPI
from knowledge.api import router as knowledge_router

api = NinjaAPI(title="RFP System API", version="1.0.0")
api.add_router("/knowledge/", knowledge_router)