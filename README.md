# Python_Data_Pipeline

A small batch ETL script in Python. It reads every CSV in a source folder, flattens any nested values, drops duplicate rows by an ID column, shrinks the column types, and writes a cleaned CSV to an output folder. The repo ships with a mock dataset (100 order rows, 12 of them duplicates) so you can run it straight away.

It is synchronous and single-process. There is no config file and no tests.

## Requirements

- Python 3 (the committed `.pyc` files are from 3.13; a test run on 3.11 worked without problems)
- `pandas` and `numpy` (see `requirements.txt`, which asks for `pandas>=2.0.0` and `numpy>=1.24.0`)

```bash
pip install -r requirements.txt
```

## Running it

```bash
python main.py
```

`main.py` has no arguments. The folders are hardcoded to `./mock_source` and `./mock_output`, and the dedupe key is hardcoded to `transaction_id`. To use your own data, edit those values in `main.py` (or build `AutomatedDataPipeline` yourself, see below).

Each run does this:

1. Overwrites `mock_source/third_party_orders.csv` with freshly generated test data: 88 unique rows (`TXN_1001` to `TXN_10088`, `amount = 150.50 * i`) plus 12 repeats of the first 12 rows. Every row has the same JSON string in `user_metadata`.
2. Runs the pipeline over every `*.csv` in `mock_source`.
3. Writes `mock_output/processed_third_party_orders.csv`.

Expected log output for the mock data:

```
Guardrail Check Complete. Eliminated 12 anomalies (12.00% anomaly rate).
Optimized layout footprint from 0.02MB to 0.01MB.
Pipeline successfully written destination: ./mock_output/processed_third_party_orders.csv
```

The output file has 88 data rows. A run in a scratch copy produced a file identical to the `mock_output` one in the repo.

To use the pipeline from your own code:

```python
from src.orchestrator import AutomatedDataPipeline

AutomatedDataPipeline(
    source_directory="path/to/csvs",
    output_directory="path/to/out",
    identity_keys=["transaction_id"],   # columns that identify a record
).run_pipeline()
```

## Layout

```
main.py                 generates the mock CSV, builds and runs the pipeline
src/orchestrator.py     AutomatedDataPipeline: file discovery, per-file flow, writing output
src/parser.py           RecursiveNestedParser: flattens dicts/lists into one level
src/ingestion.py        DataIngestionGuardrail: duplicate filtering
src/optimizer.py        MemoryOptimizationEngine: dtype downcasting
mock_source/            input CSV (regenerated every run)
mock_output/            output CSV
requirements.txt
```

## How it works

`AutomatedDataPipeline.run_pipeline()` globs `*.csv` in the source directory. If there are none it logs a warning and returns. For each file it calls `process_file`:

1. Extract: `pd.read_csv`, then convert the frame to a list of dicts.
2. Flatten: each record goes through `RecursiveNestedParser.flatten_nested_structure`. Nested dict keys are joined with `_` (`a: {b: 1}` becomes `a_b`), and list items get their index (`tags_0`, `tags_1`).
3. Deduplicate: `DataIngestionGuardrail.filter_duplicates` builds a string from the `identity_keys` values (each one stringified, stripped and lowercased, joined with `|`), hashes it with Python's `hash()`, and keeps only the first record for each hash. It logs how many were dropped and the percentage.
4. Optimize: `MemoryOptimizationEngine.optimize_dataframe_layout` picks a smaller dtype per column. Integer columns go to int8, int16 or int32 if the min and max fit. Float columns go to float32 if they are in range. Non-numeric columns become `category` when fewer than half the values are unique. It logs memory use before and after.
5. Load: the frame is written to `<output_dir>/processed_<original filename>` with `index=False`.

Error handling is a `try/except` around each file in `run_pipeline`. If a file fails, the error is logged and the loop moves on to the next file. Nothing is retried and no partial output is written for that file.

## Things to know

- The flattening step does nothing for the mock data. `read_csv` returns `user_metadata` as a plain string, and the parser only expands real dicts and lists, so the JSON string is never parsed. The output still has the original three columns (`transaction_id`, `amount`, `user_metadata`). Flattening would only matter if you parse the JSON yourself first or call the parser on dict/list data directly.
- Dedupe state (`seen_signatures`) lives on the pipeline object and is shared across files in a run. A `transaction_id` that appears in two different CSVs is kept only in whichever file is processed first.
- Dedupe compares hashes, not the keys themselves, so a hash collision would drop a non-duplicate row. Python salts string hashes per process, so the hash is only stable within one run. That is fine here because the set is never saved, but it is not a persistent signature.
- Missing key values become the string `nan` and are treated as equal to each other.
- The float32 downcast is lossy for values with more precision than float32 holds. Fine for the mock amounts, worth knowing for real money columns.
- `src/__pycache__/*.pyc` files are committed and there is no `.gitignore`.
