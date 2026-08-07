from functools import lru_cache

from fastapi import Depends

from aggregation.result_aggregator import ResultAggregator
from assessment.biodiversity_metrics import PlaceholderBiodiversityEngine
from assessment.ecological_assessment import EcologicalAssessmentEngine
from classification.classification_engine import PlaceholderClassificationEngine
from confidence.confidence_engine import PlaceholderConfidenceEngine
from controllers.analyze_controller import AnalyzeController
from controllers.assess_controller import AssessController
from controllers.classify_controller import ClassifyController
from controllers.identify_controller import IdentifyController
from controllers.preprocess_controller import PreprocessController
from controllers.status_controller import StatusController
from controllers.upload_controller import UploadController
from identification.taxonomy_engine import PlaceholderTaxonomyEngine
from interfaces.data_repository import IDataRepository
from preprocessing.sequence_processor import SequenceProcessor
from services.analysis_service import AnalysisService
from services.assessment_service import AssessmentService
from services.classification_service import ClassificationService
from services.confidence_service import ConfidenceService
from services.identification_service import IdentificationService
from services.preprocessing_service import PreprocessingService
from services.status_service import StatusService
from services.upload_service import UploadService
from storage.in_memory_repository import InMemoryRepository


@lru_cache
def get_repository() -> IDataRepository:
    # TODO:
    # Swap InMemoryRepository for a real database-backed implementation of
    # IDataRepository once the database technology is finalized.
    return InMemoryRepository()


@lru_cache
def get_preprocessor() -> SequenceProcessor:
    return SequenceProcessor()


@lru_cache
def get_taxonomy_engine() -> PlaceholderTaxonomyEngine:
    return PlaceholderTaxonomyEngine()


@lru_cache
def get_classification_engine() -> PlaceholderClassificationEngine:
    return PlaceholderClassificationEngine()


@lru_cache
def get_biodiversity_engine() -> PlaceholderBiodiversityEngine:
    return PlaceholderBiodiversityEngine()


@lru_cache
def get_ecological_engine() -> EcologicalAssessmentEngine:
    return EcologicalAssessmentEngine()


@lru_cache
def get_confidence_engine() -> PlaceholderConfidenceEngine:
    return PlaceholderConfidenceEngine()


@lru_cache
def get_result_aggregator() -> ResultAggregator:
    return ResultAggregator()


def get_upload_service(repository: IDataRepository = Depends(get_repository)) -> UploadService:
    return UploadService(repository)


def get_preprocessing_service(
    repository: IDataRepository = Depends(get_repository),
    preprocessor: SequenceProcessor = Depends(get_preprocessor),
) -> PreprocessingService:
    return PreprocessingService(repository, preprocessor)


def get_identification_service(
    repository: IDataRepository = Depends(get_repository),
    taxonomy_engine: PlaceholderTaxonomyEngine = Depends(get_taxonomy_engine),
) -> IdentificationService:
    return IdentificationService(repository, taxonomy_engine)


def get_classification_service(
    repository: IDataRepository = Depends(get_repository),
    classification_engine: PlaceholderClassificationEngine = Depends(get_classification_engine),
) -> ClassificationService:
    return ClassificationService(repository, classification_engine)


def get_assessment_service(
    repository: IDataRepository = Depends(get_repository),
    biodiversity_engine: PlaceholderBiodiversityEngine = Depends(get_biodiversity_engine),
    ecological_engine: EcologicalAssessmentEngine = Depends(get_ecological_engine),
) -> AssessmentService:
    return AssessmentService(repository, biodiversity_engine, ecological_engine)


def get_confidence_service(
    confidence_engine: PlaceholderConfidenceEngine = Depends(get_confidence_engine),
) -> ConfidenceService:
    return ConfidenceService(confidence_engine)


def get_analysis_service(
    repository: IDataRepository = Depends(get_repository),
    preprocessing_service: PreprocessingService = Depends(get_preprocessing_service),
    identification_service: IdentificationService = Depends(get_identification_service),
    classification_service: ClassificationService = Depends(get_classification_service),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    confidence_service: ConfidenceService = Depends(get_confidence_service),
    aggregator: ResultAggregator = Depends(get_result_aggregator),
) -> AnalysisService:
    return AnalysisService(
        repository,
        preprocessing_service,
        identification_service,
        classification_service,
        assessment_service,
        confidence_service,
        aggregator,
    )


def get_status_service(repository: IDataRepository = Depends(get_repository)) -> StatusService:
    return StatusService(repository)


def get_upload_controller(service: UploadService = Depends(get_upload_service)) -> UploadController:
    return UploadController(service)


def get_preprocess_controller(
    service: PreprocessingService = Depends(get_preprocessing_service),
) -> PreprocessController:
    return PreprocessController(service)


def get_identify_controller(
    service: IdentificationService = Depends(get_identification_service),
) -> IdentifyController:
    return IdentifyController(service)


def get_classify_controller(
    service: ClassificationService = Depends(get_classification_service),
) -> ClassifyController:
    return ClassifyController(service)


def get_assess_controller(service: AssessmentService = Depends(get_assessment_service)) -> AssessController:
    return AssessController(service)


def get_analyze_controller(service: AnalysisService = Depends(get_analysis_service)) -> AnalyzeController:
    return AnalyzeController(service)


def get_status_controller(service: StatusService = Depends(get_status_service)) -> StatusController:
    return StatusController(service)
