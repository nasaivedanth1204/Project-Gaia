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

    # ------------------------------------------------------------------
    # Reference / seed collections
    #
    # The seed database (data/seed/*.json) holds ~20 interconnected
    # collections. Rather than 40+ bespoke methods, collections are
    # addressed generically and the entities named in the specification
    # get thin, explicit accessors on top. A future MongoDB or SQL
    # implementation only has to satisfy these four primitives.
    # ------------------------------------------------------------------

    @abstractmethod
    def save_records(self, collection: str, records: List[Dict[str, Any]]) -> None:
        """Replace the contents of a collection."""

    @abstractmethod
    def get_record(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Fetch one record by its primary key."""

    @abstractmethod
    def list_records(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List records, optionally filtered by exact field match.

        Filter values may be a scalar (equality) or a list (membership).
        """

    @abstractmethod
    def count_records(self, collection: str) -> int: ...

    @abstractmethod
    def list_collections(self) -> List[str]: ...

    # ------------------------------------------------------------------
    # Named accessors for the entities called out in the specification.
    # These are conveniences over the generic API above.
    # ------------------------------------------------------------------

    @abstractmethod
    def save_organism(self, organism: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_organism(self, organism_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def save_analysis(self, analysis: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def save_assessment(self, assessment: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]: ...
