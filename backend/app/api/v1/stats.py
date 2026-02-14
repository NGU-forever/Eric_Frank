"""
统计相关API
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.database import User, Customer, OutreachLog, Conversation, StatsDaily
from app.models.schemas import StatsResponse, DashboardStats
from app.api.v1.auth import get_current_active_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取仪表板统计数据"""
    today = datetime.utcnow().date()
    week_ago = (datetime.utcnow() - timedelta(days=7)).date()
    month_ago = (datetime.utcnow() - timedelta(days=30)).date()

    # Get or create stats for each period
    today_stats = _get_or_create_stats(db, current_user.id, today)
    week_stats = _get_or_create_stats(db, current_user.id, week_ago)
    month_stats = _get_or_create_stats(db, current_user.id, month_ago)

    # Calculate conversion rate
    total_messages = today_stats.emails_sent + today_stats.whatsapp_sent
    conversion_rate = (today_stats.converted_customers / total_messages * 100) if total_messages > 0 else 0

    # Calculate average response time (mock for now)
    avg_response_time = 2.5  # hours

    return DashboardStats(
        today=today_stats,
        week=week_stats,
        month=month_stats,
        conversion_rate=conversion_rate,
        avg_response_time=avg_response_time
    )


@router.get("/daily", response_model=StatsResponse)
async def get_daily_stats(
    date: datetime = Query(None, description="Date (defaults to today)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取指定日期的统计"""
    target_date = date.date() if date else datetime.utcnow().date()
    stats = _get_or_create_stats(db, current_user.id, target_date)

    return stats


@router.get("/trends")
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取趋势数据"""
    end_date = datetime.utcnow().date()
    start_date = (datetime.utcnow() - timedelta(days=days)).date()

    stats = db.query(StatsDaily).filter(
        StatsDaily.user_id == current_user.id,
        StatsDaily.date >= start_date,
        StatsDaily.date <= end_date
    ).order_by(StatsDaily.date).all()

    return {
        "days": days,
        "stats": [
            {
                "date": s.date.isoformat(),
                "new_customers": s.new_customers,
                "emails_sent": s.emails_sent,
                "whatsapp_sent": s.whatsapp_sent,
                "emails_replied": s.emails_replied,
                "conversions": s.converted_customers
            }
            for s in stats
        ]
    }


@router.get("/by-platform")
async def get_stats_by_platform(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """按平台获取统计"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Customer counts by platform
    platform_stats = db.query(
        Customer.platform,
        func.count(Customer.id).label("count")
    ).filter(
        Customer.created_at >= start_date
    ).group_by(Customer.platform).all()

    return {
        "platforms": [
            {
                "platform": stat.platform,
                "count": stat.count
            }
            for stat in platform_stats
        ]
    }


@router.get("/by-country")
async def get_stats_by_country(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """按国家获取统计"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Customer counts by country
    country_stats = db.query(
        Customer.country,
        func.count(Customer.id).label("count")
    ).filter(
        Customer.created_at >= start_date
    ).group_by(Customer.country).all()

    # Sort by count
    country_stats = sorted(country_stats, key=lambda x: x.count, reverse=True)

    return {
        "countries": [
            {
                "country": stat.country or "Unknown",
                "count": stat.count
            }
            for stat in country_stats[:20]
        ]
    }


@router.get("/conversion-funnel")
async def get_conversion_funnel(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取转化漏斗数据"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Funnel stages
    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.created_at >= start_date
    ).scalar()

    contacted = db.query(func.count(OutreachLog.id.distinct())).filter(
        OutreachLog.created_at >= start_date,
        OutreachLog.status.in_(["sent", "delivered", "opened", "replied"])
    ).scalar()

    engaged = db.query(func.count(Conversation.id.distinct())).filter(
        Conversation.created_at >= start_date
    ).scalar()

    converted = db.query(func.count(Customer.id)).filter(
        Customer.created_at >= start_date,
        Customer.status == "converted"
    ).scalar()

    return {
        "stages": [
            {"name": "Total Customers", "value": total_customers},
            {"name": "Contacted", "value": contacted},
            {"name": "Engaged", "value": engaged},
            {"name": "Converted", "value": converted}
        ],
        "conversion_rates": [
            {"stage": "Contacted", "rate": (contacted / total_customers * 100) if total_customers > 0 else 0},
            {"stage": "Engaged", "rate": (engaged / contacted * 100) if contacted > 0 else 0},
            {"stage": "Converted", "rate": (converted / engaged * 100) if engaged > 0 else 0},
        ]
    }


def _get_or_create_stats(db: Session, user_id: int, date):
    """获取或创建统计数据"""
    stats = db.query(StatsDaily).filter(
        StatsDaily.user_id == user_id,
        StatsDaily.date == date
    ).first()

    if not stats:
        # Create default stats
        stats = StatsDaily(
            user_id=user_id,
            date=date
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)

    return stats
