from typing import Annotated, TypeAlias
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import require_admin, get_password_hash
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.pydantic import UserCreateRequest, UserRole

router = APIRouter(prefix="/api/admin", tags=["Administration"])

DbSession: TypeAlias = Annotated[Session, Depends(get_db)]
CurrentAdmin: TypeAlias = Annotated[dict, Depends(require_admin)]

@router.get("/audit-logs")
def get_audit_logs(db: DbSession, _admin: CurrentAdmin):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return {"status": "success", "data": logs}

@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_new_user(
    payload: UserCreateRequest, 
    db: DbSession, 
    admin_user: CurrentAdmin # <--- Enforces Admin-Only RBAC
):
    """
    Allows users with the 'admin' role to register new operational system accounts.
    """
    # 1. Validate the role payload against system configurations
    if payload.role not in UserRole:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid role assignment target."
        )

    # 2. Check if username is already taken
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered within system."
        )

    # 3. Create, hash, and persist new user
    new_user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role.value
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "status": "user_created",
        "username": new_user.username,
        "role": new_user.role
    }

@router.get("/users", status_code=status.HTTP_200_OK)
def list_system_users(
    db: DbSession,
    admin_user: CurrentAdmin
):
    """
    Returns a list of all active operational accounts within the SCADA system.
    """
    users = db.query(User).all()
    
    # Format response payload cleanly without leaking private password hashes
    return [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        for user in users
    ]


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_system_user(
    user_id: int,
    db: DbSession,
    admin_user: CurrentAdmin
):
    """
    Permanently deletes an operational user account by ID.
    """
    # 1. Locate the target account
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user account not found."
        )
        
    # 2. Prevent self-deletion (Safeguard so the admin doesn't lock themselves out)
    if user_to_delete.username == admin_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrative self-deletion is protected to prevent system lockout."
        )
        
    # 3. Purge account
    db.delete(user_to_delete)
    db.commit()
    
    return {
        "status": "user_deleted",
        "message": f"Account belonging to '{user_to_delete.username}' successfully purged."
    }