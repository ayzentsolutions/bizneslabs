import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import AuditLog
async def record_audit(db:AsyncSession,organization_id:UUID|None,user_id:UUID|None,action:str,resource_type:str,resource_id:str|None=None,metadata:dict|None=None):
    db.add(AuditLog(organization_id=organization_id,user_id=user_id,action=action,resource_type=resource_type,resource_id=resource_id,metadata_json=json.dumps(metadata or {},default=str)))
