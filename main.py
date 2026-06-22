import os
import json
import logging
import pandas as pd
from src.orchestrator import AutomatedDataPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    src_dir, out_dir = "./mock_source", "./mock_output"
    os.makedirs(src_dir, exist_ok=True)
    
    # Generate mock test file containing anomalies
    nested_metadata_sample = json.dumps({"transaction": {"type": "b2b", "risk_profile": "low"}})
    base_data = [{"transaction_id": f"TXN_100{i}", "amount": 150.50 * i, "user_metadata": nested_metadata_sample} for i in range(1, 89)]
    duplicates = [{"transaction_id": f"TXN_100{i}", "amount": 150.50 * i, "user_metadata": nested_metadata_sample} for i in range(1, 13)]
    
    pd.DataFrame(base_data + duplicates).to_csv(f"{src_dir}/third_party_orders.csv", index=False)
    
    # Initialize and execute modular architectural pipeline
    pipeline = AutomatedDataPipeline(
        source_directory=src_dir, 
        output_directory=out_dir, 
        identity_keys=["transaction_id"]
    )
    pipeline.run_pipeline()