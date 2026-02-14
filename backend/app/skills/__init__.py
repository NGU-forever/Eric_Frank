"""
Skills package - imports all skills for registration
"""
import logging

logger = logging.getLogger(__name__)

# Define __all__ first to append successfully imported skills
__all__ = []

try:
    from app.skills.skill_social_scraper import SocialScraperSkill
    __all__.append("SocialScraperSkill")
except ImportError as e:
    logger.warning(f"Failed to import SocialScraperSkill: {e}")

try:
    from app.skills.skill_data_cleaner import DataCleanerSkill
    __all__.append("DataCleanerSkill")
except ImportError as e:
    logger.warning(f"Failed to import DataCleanerSkill: {e}")

try:
    from app.skills.skill_excel_reader import ExcelReaderSkill
    __all__.append("ExcelReaderSkill")
except ImportError as e:
    logger.warning(f"Failed to import ExcelReaderSkill: {e}")

try:
    from app.skills.skill_message_generator import MessageGeneratorSkill, BulkMessageGeneratorSkill
    __all__.extend(["MessageGeneratorSkill", "BulkMessageGeneratorSkill"])
except ImportError as e:
    logger.warning(f"Failed to import MessageGeneratorSkill: {e}")

try:
    from app.skills.skill_auto_sender import AutoSenderSkill, ScheduleOutreachSkill
    __all__.extend(["AutoSenderSkill", "ScheduleOutreachSkill"])
except ImportError as e:
    logger.warning(f"Failed to import AutoSenderSkill: {e}")

try:
    from app.skills.skill_ai_reply import AIReplySkill, IntentAnalysisSkill
    __all__.extend(["AIReplySkill", "IntentAnalysisSkill"])
except ImportError as e:
    logger.warning(f"Failed to import AIReplySkill: {e}")

try:
    from app.skills.skill_monitor import MonitorSkill, TakeoverSkill, AlertSkill
    __all__.extend(["MonitorSkill", "TakeoverSkill", "AlertSkill"])
except ImportError as e:
    logger.warning(f"Failed to import MonitorSkill: {e}")

try:
    from app.skills.skill_rag import RagSkill
    __all__.append("RagSkill")
except ImportError as e:
    logger.warning(f"Failed to import RagSkill: {e}")
