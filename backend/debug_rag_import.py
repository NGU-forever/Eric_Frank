
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from app.skills.skill_rag import RagSkill
    print("RagSkill imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Exception: {e}")
