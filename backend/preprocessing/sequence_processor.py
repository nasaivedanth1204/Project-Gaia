import re
from typing import Any, Dict, List

from interfaces.preprocessing_engine import IPreprocessingEngine

# TODO:
# Replace with real primer/marker reference sequences (16S/18S/COI/ITS)
# sourced from a curated database instead of illustrative placeholders.
KNOWN_MARKERS = {
    "16S": re.compile(r"AGAGTTTGATC", re.IGNORECASE),
    "18S": re.compile(r"TACCTGGTTGATCCTGCC", re.IGNORECASE),
    "COI": re.compile(r"TTTCTACAAATCATAAAGATATTGG", re.IGNORECASE),
}


class SequenceProcessor(IPreprocessingEngine):
    def clean_sequence(self, sequence: str) -> str:
        return sequence.strip().upper()

    def remove_noise(self, sequence: str) -> str:
        # TODO:
        # Replace with a real noise-removal / quality-trimming algorithm
        # (e.g. sliding-window quality trimming, adapter/primer removal).
        cleaned = re.sub(r"[^ACGTN]", "", sequence)
        cleaned = re.sub(r"N{5,}", "", cleaned)
        return cleaned

    def normalize_sequence(self, sequence: str) -> str:
        return sequence.replace("U", "T").replace("-", "")

    def detect_markers(self, sequence: str) -> List[str]:
        # TODO:
        # Replace with real marker-gene detection via alignment against
        # reference primers or HMM profiles.
        return [name for name, pattern in KNOWN_MARKERS.items() if pattern.search(sequence)]

    def extract_features(self, sequence: str) -> Dict[str, Any]:
        # TODO:
        # Replace with real feature extraction (k-mer frequency vectors,
        # GC-content sliding windows, embeddings from a trained model).
        length = len(sequence)
        n_count = sequence.count("N")
        gc_count = sum(1 for base in sequence if base in "GC")
        return {
            "length": length,
            "gc_content": round(gc_count / length, 4) if length else 0.0,
            "n_count": n_count,
            "completeness": round(1 - (n_count / length), 4) if length else 0.0,
        }
