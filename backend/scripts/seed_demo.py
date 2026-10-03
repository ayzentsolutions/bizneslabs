import asyncio
import os
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import Agent, InventoryItem, InventoryStatus, Membership, Organization, Role, User, KnowledgeDocument
from app.rag.embeddings import DeterministicEmbeddingProvider
from app.rag.ingestion import index_document

async def seed():
    password = os.environ.get("DEMO_ADMIN_PASSWORD")
    if not password:
        raise RuntimeError("Set DEMO_ADMIN_PASSWORD before running the demo seed")
    async with SessionLocal() as db:
        org=Organization(name="ABC Motors",industry="Car Showroom",country="India",timezone="Asia/Kolkata")
        user=User(email="admin@abcmotors.example",password_hash=hash_password(password),full_name="ABC Motors Admin")
        db.add_all([org,user])
        await db.flush()
        db.add(Membership(user_id=user.id,organization_id=org.id,role=Role.OWNER))
        db.add(Agent(
            organization_id=org.id,name="Alex — AI Sales Executive",role="AI Sales Executive",
            description="Sales and test-drive assistant for ABC Motors.",language="en-IN",
            greeting="Namaste! I am Alex from ABC Motors. How can I help you today?",
            personality="Helpful, concise, professional and transparent.",
            system_instructions="Never invent inventory, prices, customer data or appointment availability. Use authorized tools for live facts.",
        ))
        rows=[
            ("Hyundai","Creta","SX","White",1520000,"Petrol","Automatic",2026,InventoryStatus.AVAILABLE,1),
            ("Hyundai","Creta","SX","Black",1520000,"Petrol","Automatic",2026,InventoryStatus.BOOKED,1),
            ("Hyundai","Venue","S(O)","White",1280000,"Petrol","Automatic",2026,InventoryStatus.AVAILABLE,1),
            ("Hyundai","Verna","SX","Red",1420000,"Petrol","Automatic",2026,InventoryStatus.SOLD,0),
        ]
        for row in rows:
            db.add(InventoryItem(
                organization_id=org.id,brand=row[0],model=row[1],variant=row[2],color=row[3],
                price=row[4],fuel_type=row[5],transmission=row[6],year=row[7],status=row[8],stock_quantity=row[9],
            ))
        doc=KnowledgeDocument(
            organization_id=org.id,title="ABC Motors Sales FAQ",source_type="TEXT",
            extracted_text="ABC Motors offers Hyundai vehicles and test drives. Inventory and appointment availability must be verified live before confirmation.",
            status="READY",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        await index_document(db,org.id,doc,DeterministicEmbeddingProvider())
        print("ABC Motors demo tenant seeded.")

if __name__=="__main__":
    asyncio.run(seed())
