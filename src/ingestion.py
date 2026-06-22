import logging
from typing import List, Dict, Any, Set
logger = logging.getLogger("DataPipelineEngine")

class DataIngestionGuardrail:
    def __init__(self):
        self.seen_signatures: Set[int] = set()

    def generate_deterministic_hash(self, row: Dict[str, Any], identity_keys: List[str]) -> int:
        try:
            identity_string = "|".join(str(row.get(key, "")).strip().lower() for key in identity_keys)
            return hash(identity_string)
        except Exception as e:
            logger.error(f"Failed to generate deterministic hash for row: {e}")
            return hash(str(row))

    def filter_duplicates(self, record_stream: List[Dict[str, Any]], identity_keys: List[str]) -> List[Dict[str, Any]]:
        cleaned_records = []
        duplicate_count = 0
        total_records = len(record_stream)

        for record in record_stream:
            record_hash = self.generate_deterministic_hash(record, identity_keys)
            if record_hash in self.seen_signatures:
                duplicate_count += 1
                continue
            self.seen_signatures.add(record_hash)
            cleaned_records.append(record)

        if total_records > 0:
            anomaly_rate = (duplicate_count / total_records) * 100
            logger.info(f"Guardrail Check Complete. Eliminated {duplicate_count} anomalies ({anomaly_rate:.2f}% anomaly rate).")
        return cleaned_records