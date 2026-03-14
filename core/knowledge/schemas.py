from ninja import Schema
from datetime import datetime
from typing import Optional

class AssetOut(Schema):
    id: str
    title: str
    asset_type: str
    status: str
    chunk_count: int
    error_message: str
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

class AssetListOut(Schema):
    id: str
    title: str
    asset_type: str
    status: str
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True