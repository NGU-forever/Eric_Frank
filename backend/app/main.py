"""
FastAPI应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.db import init_db
from app.core.agent import get_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # Initialize database
    init_db()

    # Register skills
    if not settings.START_MINIMAL:
        import app.skills  # noqa
        agent = get_agent()
        from app.core.skill_base import SkillRegistry
        skills = SkillRegistry.list_all()
        print(f"Registered {len(skills)} skills:")
        for name, skill_class in skills.items():
            print(f"  - {name}: {skill_class.display_name}")
            agent.register_skill(skill_class())

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered B2B customer acquisition and automation system",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Trade AI Agent API is running"
    }


# Import routers
from app.api.v1 import auth, workflow, skill, customer, conversation, stats, admin

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(workflow.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(skill.router, prefix="/api/v1/skills", tags=["Skills"])
app.include_router(customer.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(conversation.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Statistics"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


def main():
    """主函数"""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
