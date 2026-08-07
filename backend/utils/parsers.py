import csv
import io
from typing import Dict, List

from utils.id_generator import generate_id


def parse_fasta(content: str) -> List[Dict]:
    records = []
    blocks = [b for b in content.split(">") if b.strip()]
    for block in blocks:
        lines = block.strip().splitlines()
        header = lines[0].strip() if lines else "unknown"
        sequence = "".join(line.strip() for line in lines[1:])
        records.append(
            {
                "sequence_id": generate_id("seq"),
                "header": header,
                "sequence": sequence.upper(),
                "length": len(sequence),
            }
        )
    return records


def parse_csv(content: str) -> List[Dict]:
    records = []
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        normalized = {(k or "").strip().lower(): v for k, v in row.items() if k}
        sequence = (normalized.get("sequence") or "").strip()
        header = normalized.get("id") or normalized.get("header") or generate_id("seq")
        records.append(
            {
                "sequence_id": generate_id("seq"),
                "header": header,
                "sequence": sequence.upper(),
                "length": len(sequence),
            }
        )
    return records


def parse_txt(content: str) -> List[Dict]:
    records = []
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    for line in lines:
        records.append(
            {
                "sequence_id": generate_id("seq"),
                "header": generate_id("seq"),
                "sequence": line.upper(),
                "length": len(line),
            }
        )
    return records


def parse_sequences(file_type: str, content: str) -> List[Dict]:
    if file_type == "fasta":
        return parse_fasta(content)
    if file_type == "csv":
        return parse_csv(content)
    return parse_txt(content)
