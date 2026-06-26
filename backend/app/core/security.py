from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.schemas.pydantic import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plaintext password."""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- RBAC Dependencies ---
def require_operator(user: dict = Depends(get_current_user)):
    """Can view telemetry and alarms (All roles can do this)."""
    if user["role"] not in [UserRole.OPERATOR.value, UserRole.DISPATCHER.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    return user

def require_dispatcher(user: dict = Depends(get_current_user)):
    """Strictly for operating physical infrastructure."""
    if user["role"] not in [UserRole.DISPATCHER.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Grid operations are restricted to dispatchers and admins.")
    return user

def require_admin(user: dict = Depends(get_current_user)):
    """Strictly for system auditing and user management."""
    if user["role"] != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Administrator privileges required.")
    return user