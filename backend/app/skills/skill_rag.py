import os
from typing import Dict, Any, List, Optional
from pydantic import Field

from app.core.skill_base import BaseSkill, register_skill
from app.config import settings
from app.core.context import ExecutionContext

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embedding imports
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import DashScopeEmbeddings
except ImportError:
    pass


@register_skill
class RagSkill(BaseSkill):
    """
    RAG (Retrieval-Augmented Generation) Skill
    
    Capabilities:
    1. Add text/documents to knowledge base
    2. Retrieve relevant context for queries
    3. Management of knowledge base collections
    """
    
    name: str = "rag_skill"
    display_name: str = "RAG知识库"
    description: str = "管理知识库并检索相关信息以增强AI回复"
    icon: str = "Document"
    version: str = "1.0.0"
    
    # Configuration
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "query", "clear"],
                "description": "操作类型：添加知识(add)、查询(query)或清空(clear)"
            },
            "text": {
                "type": "string",
                "description": "要添加的文本内容或查询语句"
            },
            "collection_name": {
                "type": "string",
                "default": "default",
                "description": "知识库集合名称"
            },
            "metadata": {
                "type": "object",
                "description": "元数据（仅用于添加操作）"
            },
            "top_k": {
                "type": "integer",
                "default": 3,
                "description": "返回的最相关文档数量"
            }
        },
        "required": ["action"]
    }
    
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "documents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "metadata": {"type": "object"},
                        "score": {"type": "number"}
                    }
                }
            }
        }
    }

    def _get_embeddings(self):
        """Get embedding model based on configuration"""
        if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE
            )
        elif settings.AI_PROVIDER == "tongyi" and settings.TONGYI_API_KEY:
            # Fallback to OpenAI compatible interface or DashScope
            # DashScopeEmbeddings requires 'dashscope' package usually, 
            # but langchain-community wraps it. 
            # If not available, we might default to a simple one or raise error.
            return DashScopeEmbeddings(
                dashscope_api_key=settings.TONGYI_API_KEY,
                model="text-embedding-v1"
            )
        elif settings.AI_PROVIDER == "qwen" and settings.QWEN_API_KEY:
             return DashScopeEmbeddings(
                dashscope_api_key=settings.QWEN_API_KEY,
                model="text-embedding-v1"
            )
        
        # Default fallback (might require local model download)
        # return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        raise ValueError("No valid embedding provider configured. Please set API keys.")

    def _get_vectorstore(self, collection_name: str):
        """Get Chroma vector store instance"""
        embeddings = self._get_embeddings()
        persist_directory = os.path.join(settings.CHROMA_DB_DIR, collection_name)
        
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )

    async def execute(self, context: ExecutionContext, **kwargs) -> Dict[str, Any]:
        """Execute the skill"""
        action = kwargs.get("action")
        text = kwargs.get("text", "")
        collection_name = kwargs.get("collection_name", "default")
        
        try:
            if action == "add":
                if not text:
                    return {"success": False, "message": "Text is required for 'add' action"}
                
                metadata = kwargs.get("metadata", {})
                return await self._add_document(text, collection_name, metadata)
                
            elif action == "query":
                if not text:
                    return {"success": False, "message": "Text is required for 'query' action"}
                
                top_k = kwargs.get("top_k", 3)
                return await self._query_documents(text, collection_name, top_k)
                
            elif action == "clear":
                return await self._clear_collection(collection_name)
                
            else:
                return {"success": False, "message": f"Unknown action: {action}"}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False, 
                "message": str(e),
                "error_type": type(e).__name__
            }

    async def _add_document(self, text: str, collection_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add document to vector store"""
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        texts = text_splitter.split_text(text)
        
        # Create documents
        docs = [Document(page_content=t, metadata=metadata) for t in texts]
        
        # Add to vector store
        vectorstore = self._get_vectorstore(collection_name)
        vectorstore.add_documents(docs)
        vectorstore.persist()
        
        return {
            "success": True,
            "message": f"Added {len(docs)} chunks to collection '{collection_name}'",
            "count": len(docs)
        }

    async def _query_documents(self, query: str, collection_name: str, top_k: int) -> Dict[str, Any]:
        """Query vector store"""
        vectorstore = self._get_vectorstore(collection_name)
        
        # Similarity search
        results = vectorstore.similarity_search_with_score(query, k=top_k)
        
        documents = []
        for doc, score in results:
            documents.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)  # Convert numpy float to python float
            })
            
        return {
            "success": True,
            "message": f"Found {len(documents)} relevant documents",
            "documents": documents
        }

    async def _clear_collection(self, collection_name: str) -> Dict[str, Any]:
        """Clear a collection"""
        vectorstore = self._get_vectorstore(collection_name)
        vectorstore.delete_collection()
        vectorstore.persist()
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' cleared"
        }
