from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.userSchema import User

user_router = APIRouter(prefix="/api/user", tags=["用户模块"])

@user_router.post("/register")
async def register(user: User, db: AsyncSession = Depends(get_db)):
    return {"code": 0, "msg": user.username}
