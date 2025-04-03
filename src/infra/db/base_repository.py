from typing import Any

from src.infra.db.models import Base, session


class BaseRepository[T: Base]:
    def __init__(self, model: type[T]) -> None:
        self._model = model

    async def get_by_id(self, model_id: Any) -> T | None:  # noqa: ANN401
        """Get a model by ID."""
        return (
            session.query(self._model)
            .filter(getattr(self._model, "id") == model_id)  # noqa: B009
            .first()
        )

    async def save(self, model: T) -> T:
        """Create a new model."""
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    async def delete(self, model: T) -> None:
        """Delete a model."""
        session.delete(model)
        session.commit()
        session.refresh(model)

    async def get_all(self) -> list[T]:
        """Get all models."""
        return session.query(self._model).all()
