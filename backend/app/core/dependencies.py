"""
FastAPI Dependencies
"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session


# Type alias for database session dependency
DBSession = Annotated[AsyncSession, Depends(get_session)]


# Placeholder for future dependencies
# Example: Current user, AI Router, Vector Store, etc.

async def get_vector_store():
    """
    Dependency to get vector store adapter.
    TO BE IMPLEMENTED by team based on chosen vector store.
    """
    # from app.modules.rag.adapters import get_adapter
    # return get_adapter()
    raise NotImplementedError("Vector store adapter not configured")


async def get_ai_router():
    """
    Dependency to get AI router instance.
    """
    from app.ai.router import AIRouter
    return AIRouter()
