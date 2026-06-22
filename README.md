# Automated Data Pipeline & Ingestion Engine

An asynchronous, production-grade automated ETL pipeline optimized using modular Object-Oriented Design patterns in Python. 

## Key Features
- **Recursive Structural Flattening:** Traverses deeply nested unstructured JSON parameters injected into source data and normalizes them cleanly into schemas.
- **Deterministic Validation Guardrail:** Formulates a compound signature hashing loop to detect and cleanly purge targeted record duplication anomalies down to 0%.
- **Memory Layout Vectorization:** Evaluates data frame properties dynamically, automatically safely downcasting integers/floats and converting low-cardinality values to categorical types to dramatically compress memory profiles during scale transformations.

## How to execute
```bash
pip install -r requirements.txt
python main.py