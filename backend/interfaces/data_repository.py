from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IDataRepository(ABC):
    """Persistence abstraction. Swap the in-memory implementation for a real
    database-backed one (MongoDB, PostgreSQL, ...) without touching callers.
    """

    @abstractmethod
    def save_sample(self, sample_id: str, sample_data: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_sample(self, sample_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def update_sample_status(self, sample_id: str, status: str) -> None: ...

    @abstractmethod
    def save_stage_result(self, sample_id: str, stage: str, data: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_stage_result(self, sample_id: str, stage: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def save_prediction(self, sample_id: str, prediction: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_prediction(self, sample_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def get_history(self) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def list_samples(self) -> List[str]: ...
