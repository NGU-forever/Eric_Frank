"""
客户管理相关API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.database import User, Customer
from app.models.schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListResponse, SearchFilters
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    intent_level: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """列出客户"""
    query = db.query(Customer)

    # Apply filters
    if platform:
        query = query.filter(Customer.platform == platform)
    if country:
        query = query.filter(Customer.country == country)
    if category:
        query = query.filter(Customer.category == category)
    if status:
        query = query.filter(Customer.status == status)
    if intent_level:
        query = query.filter(Customer.intent_level == intent_level)
    if search:
        query = query.filter(
            (Customer.username.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )

    # Count total
    total = query.count()

    # Pagination
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return CustomerListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建客户"""
    # Check for duplicates
    existing = db.query(Customer).filter(
        Customer.username == customer.username,
        Customer.platform == customer.platform
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists")

    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取客户详情"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新客户信息"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = customer_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除客户"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted"}


@router.post("/bulk")
async def bulk_create_customers(
    customers: List[CustomerCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量创建客户"""
    created = []
    duplicates = 0

    for customer_data in customers:
        # Check for duplicates
        existing = db.query(Customer).filter(
            Customer.username == customer_data.username,
            Customer.platform == customer_data.platform
        ).first()

        if existing:
            duplicates += 1
            continue

        db_customer = Customer(**customer_data.model_dump())
        db.add(db_customer)
        db.flush()
        created.append(db_customer)

    db.commit()

    return {
        "created": len(created),
        "duplicates": duplicates,
        "customers": [c.id for c in created]
    }


@router.post("/{customer_id}/tags")
async def add_tags(
    customer_id: int,
    tags: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """为客户添加标签"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    current_tags = customer.tags_json or []
    new_tags = list(set(current_tags + tags))
    customer.tags_json = new_tags

    db.commit()

    return {"tags": new_tags}


@router.delete("/{customer_id}/tags")
async def remove_tags(
    customer_id: int,
    tags: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """从客户移除标签"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    current_tags = customer.tags_json or []
    new_tags = [t for t in current_tags if t not in tags]
    customer.tags_json = new_tags

    db.commit()

    return {"tags": new_tags}
