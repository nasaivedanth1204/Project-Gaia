import re
from typing import List

from utils.exceptions import ValidationError

ALLOWED_EXTENSIONS = {"fasta", "fa", "fna", "csv", "txt"}
VALID_DNA_PATTERN = re.compile(r"^[ACGTUNRYSWKMBDHVacgtunryswkmbdhv\-\.\s]+$")
VALID_DNA_CHARS = set("ACGTUNRYSWKMBDHVacgtunryswkmbdhv-. \t")


def validate_file_extension(filename: str) -> str:
    if not filename or "." not in filename:
        raise ValidationError(f"File '{filename}' is missing a valid extension.")
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '.{extension}'. Allowed types: {sorted(ALLOWED_EXTENSIONS)}"
        )
    return extension


def validate_dna_sequence(sequence: str) -> None:
    if not sequence or not sequence.strip():
        raise ValidationError("Empty DNA sequence provided.")
    cleaned = sequence.strip()
    if not VALID_DNA_PATTERN.match(cleaned):
        invalid_chars = sorted(set(cleaned) - VALID_DNA_CHARS)
        raise ValidationError(f"Sequence contains invalid characters: {invalid_chars}")


def validate_fasta_content(content: str) -> List[str]:
    errors: List[str] = []
    if not content or not content.strip():
        errors.append("FASTA content is empty.")
        return errors
    if not content.lstrip().startswith(">"):
        errors.append("FASTA content must start with a header line beginning with '>'.")
    blocks = [b for b in content.split(">") if b.strip()]
    if not blocks:
        errors.append("No valid FASTA records found.")
    for block in blocks:
        lines = block.strip().splitlines()
        header = lines[0] if lines else ""
        sequence = "".join(lines[1:]).strip()
        if not header:
            errors.append("A FASTA record is missing a header.")
        if not sequence:
            errors.append(f"Record '{header}' has no sequence data.")
        else:
            try:
                validate_dna_sequence(sequence)
            except ValidationError as exc:
                errors.append(f"Record '{header}': {exc.message}")
    return errors


def validate_csv_content(content: str) -> List[str]:
    errors: List[str] = []
    if not content or not content.strip():
        errors.append("CSV content is empty.")
        return errors
    lines = [line for line in content.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        errors.append("CSV must contain a header row and at least one data row.")
        return errors
    header = [col.strip().lower() for col in lines[0].split(",")]
    if "sequence" not in header:
        errors.append("CSV must contain a 'sequence' column.")
    return errors


def validate_txt_content(content: str) -> List[str]:
    errors: List[str] = []
    if not content or not content.strip():
        errors.append("TXT content is empty.")
        return errors
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    for i, line in enumerate(lines, start=1):
        try:
            validate_dna_sequence(line)
        except ValidationError as exc:
            errors.append(f"Line {i}: {exc.message}")
    return errors


def validate_upload(filename: str, content: str) -> str:
    extension = validate_file_extension(filename)
    file_type = "fasta" if extension in ("fa", "fna") else extension

    if file_type == "fasta":
        errors = validate_fasta_content(content)
    elif file_type == "csv":
        errors = validate_csv_content(content)
    else:
        errors = validate_txt_content(content)

    if errors:
        raise ValidationError("Validation failed for uploaded file.", errors=errors)
    return file_type
