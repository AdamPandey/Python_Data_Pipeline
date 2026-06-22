import os
import glob
import logging
from typing import List
import pandas as pd

from src.ingestion import DataIngestionGuardrail
from src.parser import RecursiveNestedParser
from src.optimizer import MemoryOptimizationEngine

logger = logging.getLogger("DataPipelineEngine")

class AutomatedDataPipeline:
    def __init__(self, source_directory: str, output_directory: str, identity_keys: List[str]):
        self.source_dir = source_directory
        self.output_dir = output_directory
        self.identity_keys = identity_keys
        self.guardrail = DataIngestionGuardrail()
        self.parser = RecursiveNestedParser()

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    def extract_source_files(self) -> List[str]:
        return glob.glob(os.path.join(self.source_dir, "*.csv"))

    def process_file(self, file_path: str) -> pd.DataFrame:
        logger.info(f"Commencing extraction pipeline for target: {os.path.basename(file_path)}")
        raw_df = pd.read_csv(file_path)
        raw_records = raw_df.to_dict(orient="records")
        
        flattened_records = [self.parser.flatten_nested_structure(record) for record in raw_records]
        validated_records = self.guardrail.filter_duplicates(flattened_records, self.identity_keys)
        
        clean_df = pd.DataFrame(validated_records)
        return MemoryOptimizationEngine.optimize_dataframe_layout(clean_df)

    def run_pipeline(self) -> None:
        files_to_process = self.extract_source_files()
        if not files_to_process:
            logger.warning("Pipeline execution halted: No source datasets extracted.")
            return

        for file_path in files_to_process:
            try:
                processed_df = self.process_file(file_path)
                destination = os.path.join(self.output_dir, f"processed_{os.path.basename(file_path)}")
                processed_df.to_csv(destination, index=False)
                logger.info(f"Pipeline successfully written destination: {destination}\n")
            except Exception as e:
                logger.error(f"Critical operational error processing target file {file_path}: {e}")