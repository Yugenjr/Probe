"""Base repository implementing unit-of-work transaction management."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseRepository:
    """Encapsulates raw SQLAlchemy session logic and common transaction contexts."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
