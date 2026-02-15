"""
Skill管理相关API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.core.skill_base import SkillRegistry
from app.models.schemas import SkillMetadataResponse, SkillListResponse
from app.models.database import User
from app.api.v1.auth import get_current_active_user

router = APIRouter()


@router.get("", response_model=SkillListResponse)
async def list_skills(
    category: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """列出所有可用的Skills"""
    skills = SkillRegistry.list_all()
    categories = SkillRegistry.get_categories()

    # Filter by category if specified
    if category:
        skills = {
            name: skill_class
            for name, skill_class in skills.items()
            if skill_class.category == category
        }

    # Build response
    skill_metadata = []
    for name, skill_class in skills.items():
        skill_metadata.append({
            "name": skill_class.name,
            "display_name": skill_class.display_name,
            "description": skill_class.description,
            "category": skill_class.category,
            "version": skill_class.version,
            "config_schema": skill_class.config_schema,
            "input_schema": skill_class.input_schema,
            "output_schema": skill_class.output_schema,
            "timeout": skill_class.timeout,
            "retry_count": skill_class.retry_count,
        })

    return SkillListResponse(
        skills=skill_metadata,
        categories=sorted(categories)
    )


@router.get("/{skill_name}", response_model=SkillMetadataResponse)
async def get_skill(
    skill_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """获取Skill详情"""
    skill_class = SkillRegistry.get(skill_name)

    if not skill_class:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    return {
        "name": skill_class.name,
        "display_name": skill_class.display_name,
        "description": skill_class.description,
        "category": skill_class.category,
        "version": skill_class.version,
        "config_schema": skill_class.config_schema,
        "input_schema": skill_class.input_schema,
        "output_schema": skill_class.output_schema,
        "timeout": skill_class.timeout,
        "retry_count": skill_class.retry_count,
    }


@router.get("/categories/list")
async def list_categories(
    current_user: User = Depends(get_current_active_user)
):
    """列出所有Skill分类"""
    categories = SkillRegistry.get_categories()

    return {
        "categories": sorted(categories)
    }
