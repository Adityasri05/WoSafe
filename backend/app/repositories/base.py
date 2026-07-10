"""
WoSafe Repositories — Base Repository
Generic async CRUD repository with pagination, filtering, and soft delete.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository implementing common CRUD operations."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    # ── Read ───────────────────────────────

    async def get(self, id: UUID, include_deleted: bool = False) -> ModelType | None:
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(self, field: str, value: Any, include_deleted: bool = False) -> ModelType | None:
        """Get a single record by a specific field."""
        column = getattr(self.model, field)
        query = select(self.model).where(column == value)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        descending: bool = True,
        include_deleted: bool = False,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        """Get multiple records with pagination and optional filters."""
        query = select(self.model)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712

        if filters:
            query = self._apply_filters(query, filters)

        order_column = getattr(self.model, order_by, self.model.created_at)
        if descending:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, include_deleted: bool = False, filters: dict[str, Any] | None = None) -> int:
        """Count records matching the criteria."""
        query = select(func.count(self.model.id))
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        if filters:
            query = self._apply_filters(query, filters)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def exists(self, id: UUID) -> bool:
        """Check if a record exists."""
        query = select(func.count(self.model.id)).where(
            self.model.id == id, self.model.is_deleted == False  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one() > 0

    # ── Create ─────────────────────────────

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new record."""
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    # ── Update ─────────────────────────────

    async def update(self, id: UUID, data: dict[str, Any]) -> ModelType | None:
        """Update a record by ID."""
        instance = await self.get(id)
        if not instance:
            return None
        for key, value in data.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def bulk_update(self, ids: list[UUID], data: dict[str, Any]) -> int:
        """Bulk update records by IDs."""
        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**data)
        )
        result = await self.db.execute(stmt)
        return result.rowcount

    # ── Delete ─────────────────────────────

    async def soft_delete(self, id: UUID) -> bool:
        """Soft delete a record."""
        instance = await self.get(id)
        if not instance:
            return False
        instance.soft_delete()
        await self.db.flush()
        return True

    async def hard_delete(self, id: UUID) -> bool:
        """Permanently delete a record."""
        instance = await self.get(id, include_deleted=True)
        if not instance:
            return False
        await self.db.delete(instance)
        await self.db.flush()
        return True

    async def restore(self, id: UUID) -> ModelType | None:
        """Restore a soft-deleted record."""
        instance = await self.get(id, include_deleted=True)
        if not instance or not instance.is_deleted:
            return None
        instance.restore()
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    # ── Helpers ─────────────────────────────

    def _apply_filters(self, query: Select, filters: dict[str, Any]) -> Select:
        """Apply dynamic filters to a query."""
        for field, value in filters.items():
            if not hasattr(self.model, field):
                continue
            column = getattr(self.model, field)
            if isinstance(value, list):
                query = query.where(column.in_(value))
            elif isinstance(value, dict):
                if "gte" in value:
                    query = query.where(column >= value["gte"])
                if "lte" in value:
                    query = query.where(column <= value["lte"])
                if "like" in value:
                    query = query.where(column.ilike(f"%{value['like']}%"))
            else:
                query = query.where(column == value)
        return query
