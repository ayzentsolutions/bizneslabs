from uuid import uuid4
from app.tenancy.scope import require_tenant_id

def test_missing_tenant_is_rejected():
    from fastapi import HTTPException
    try:
        require_tenant_id(None)
        assert False
    except HTTPException as exc:
        assert exc.status_code == 403

def test_tenant_id_is_explicit():
    tenant = uuid4()
    assert require_tenant_id(tenant) == tenant
