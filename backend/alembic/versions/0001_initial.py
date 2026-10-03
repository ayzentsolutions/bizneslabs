"""Initial BiznesLabs multi-tenant schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    role = sa.Enum("SUPER_ADMIN","OWNER","ADMIN","AGENT_MANAGER","VIEWER", name="role")
    inventory_status = sa.Enum("AVAILABLE","BOOKED","SOLD","RESERVED","MAINTENANCE","OUT_OF_STOCK", name="inventorystatus")
    lead_status = sa.Enum("NEW","CONTACTED","QUALIFIED","FOLLOW_UP","CONVERTED","LOST", name="leadstatus")
    bind = op.get_bind()
    role.create(bind, checkfirst=True)
    inventory_status.create(bind, checkfirst=True)
    lead_status.create(bind, checkfirst=True)

    op.create_table("organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("industry", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("timezone", sa.String(100), nullable=False),
        sa.Column("contact_email", sa.String(320)),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", role, nullable=False))
    op.create_index("ix_memberships_org_user", "memberships", ["organization_id","user_id"], unique=True)
    op.create_table("agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False), sa.Column("role", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""), sa.Column("language", sa.String(50), nullable=False, server_default="en-IN"),
        sa.Column("greeting", sa.Text(), nullable=False, server_default=""), sa.Column("personality", sa.Text(), nullable=False, server_default=""),
        sa.Column("system_instructions", sa.Text(), nullable=False, server_default=""), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_agents_org_created","agents",["organization_id","created_at"])
    op.create_table("inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False), sa.Column("model", sa.String(100), nullable=False),
        sa.Column("variant", sa.String(100), nullable=False), sa.Column("color", sa.String(100), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False), sa.Column("fuel_type", sa.String(50), nullable=False),
        sa.Column("transmission", sa.String(50), nullable=False), sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", inventory_status, nullable=False), sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_inventory_org_status","inventory_items",["organization_id","status"])
    op.create_index("ix_inventory_org_lookup","inventory_items",["organization_id","model","variant","color"])
    op.create_table("leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False), sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(320)), sa.Column("interested_product", sa.String(200)), sa.Column("budget", sa.Integer()),
        sa.Column("source", sa.String(100), nullable=False, server_default="AI_AGENT"), sa.Column("status", lead_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_leads_org_created","leads",["organization_id","created_at"])
    op.create_index("ix_leads_org_phone","leads",["organization_id","phone"])
    op.create_table("appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL")),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL")),
        sa.Column("customer_name", sa.String(200), nullable=False), sa.Column("customer_phone", sa.String(50), nullable=False),
        sa.Column("vehicle", sa.String(200)), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="BOOKED"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_appointments_org_start","appointments",["organization_id","starts_at"])
    op.create_table("knowledge_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False), sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_uri", sa.Text()), sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_knowledge_docs_org_created","knowledge_documents",["organization_id","created_at"])
    op.create_table("knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False), sa.Column("embedding", Vector(1536)), sa.Column("chunk_index", sa.Integer(), nullable=False))
    op.create_index("ix_knowledge_chunks_org_doc","knowledge_chunks",["organization_id","document_id"])
    op.create_table("calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL")),
        sa.Column("caller_phone", sa.String(50)), sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="IN_PROGRESS"), sa.Column("outcome", sa.String(100)),
        sa.Column("transcript", sa.Text(), nullable=False, server_default=""), sa.Column("tools_used", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_calls_org_created","calls",["organization_id","created_at"])
    op.create_table("audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(100), nullable=False), sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100)), sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_audit_org_created","audit_logs",["organization_id","created_at"])

def downgrade() -> None:
    for table in ["audit_logs","calls","knowledge_chunks","knowledge_documents","appointments","leads","inventory_items","agents","memberships","users","organizations"]:
        op.drop_table(table)
    bind = op.get_bind()
    sa.Enum(name="leadstatus").drop(bind, checkfirst=True)
    sa.Enum(name="inventorystatus").drop(bind, checkfirst=True)
    sa.Enum(name="role").drop(bind, checkfirst=True)
