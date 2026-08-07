from enum import Enum


class FileType(str, Enum):
    FASTA = "fasta"
    CSV = "csv"
    TXT = "txt"


class PipelineStage(str, Enum):
    UPLOADED = "uploaded"
    PREPROCESSED = "preprocessed"
    IDENTIFIED = "identified"
    CLASSIFIED = "classified"
    ASSESSED = "assessed"
    ANALYZED = "analyzed"
