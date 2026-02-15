"""
管理后台API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.database import User, Account, TaskQueue
from app.models.schemas import (
    UserCreate, UserResponse, AccountCreate, AccountUpdate, AccountResponse
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """列出所有用户（管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建用户（管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Check for duplicates
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    from app.api.v1.auth import get_password_hash

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """列出所有账号"""
    query = db.query(Account)

    if not current_user.is_superuser:
        query = query.filter(Account.user_id == current_user.id)

    accounts = query.all()
    return accounts


@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建账号"""
    # Check for duplicates
    existing = db.query(Account).filter(
        Account.email == account.email,
        Account.account_type == account.account_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")

    db_account = Account(
        user_id=current_user.id,
        account_type=account.account_type,
        name=account.name,
        email=account.email,
        phone_number=account.phone_number,
        credentials_json=account.credentials,
        daily_limit=account.daily_limit,
        today_sent=0
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取账号详情"""
    query = db.query(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        query = query.filter(Account.user_id == current_user.id)

    account = query.first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新账号"""
    query = db.query(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        query = query.filter(Account.user_id == current_user.id)

    account = query.first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = account_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)

    return account


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除账号"""
    query = db.query(Account).filter(Account.id == account_id)

    if not current_user.is_superuser:
        query = query.filter(Account.user_id == current_user.id)

    account = query.first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()

    return {"message": "Account deleted"}


@router.get("/tasks")
async def list_tasks(
    status: str = None,
    task_type: str = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """列出任务"""
    query = db.query(TaskQueue)

    if status:
        query = query.filter(TaskQueue.status == status)
    if task_type:
        query = query.filter(TaskQueue.task_type == task_type)

    tasks = query.order_by(TaskQueue.created_at.desc()).limit(limit).all()

    return {
        "tasks": [
            {
                "id": str(t.id),
                "task_type": t.task_type,
                "status": t.status.value if t.status else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "scheduled_at": t.scheduled_at.isoformat() if t.scheduled_at else None,
                "executed_at": t.executed_at.isoformat() if t.executed_at else None,
                "error_msg": t.error_msg
            }
            for t in tasks
        ]
    }


@router.post("/system/restart")
async def restart_system(
    current_user: User = Depends(get_current_active_user)
):
    """重启系统（管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    # In production, this would trigger a restart
    return {"message": "System restart initiated"}
