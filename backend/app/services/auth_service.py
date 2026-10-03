from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import Membership, User

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, email: str, password: str) -> tuple[User, Membership]:
        result = await self.db.execute(select(User).where(User.email == email, User.active.is_(True)))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        membership_result = await self.db.execute(
            select(Membership).where(Membership.user_id == user.id).order_by(Membership.id)
        )
        membership = membership_result.scalars().first()
        if not membership:
            raise ValueError("User has no organization membership")
        return user, membership

    def issue_token(self, user: User, membership: Membership) -> str:
        return create_access_token(str(user.id), membership.role.value, str(membership.organization_id))
