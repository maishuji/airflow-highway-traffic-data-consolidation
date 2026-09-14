# Highway Traffic Data Consolidation

## Project Overview

This project implements an Extract, Transform, and Load (ETL) pipeline using Apache Airflow. It consolidates highway traffic data from different toll plazas, normalizes the source formats, validates the resulting records, and publishes the transformed output for downstream analysis.

## Getting started

Prerequisites:

- Docker Engine with Docker Compose v2
- `uv` for local dependency management and checks
- `wget` and `tar` for downloading and extracting the source archive

From the repository root:

```bash
cp .env.example .env
make extract-data
make compose-up
```

Open [http://localhost:8080](http://localhost:8080). Airflow 3 generates the local admin password on first startup; read it with `docker compose logs airflow-api-server`. If port `8080` is already in use, set `AIRFLOW_API_PORT` in `.env` and use the corresponding port.

To run the project checks locally:

```bash
make sync
make check
```

Stop the local stack with `make compose-down`.

## Technologies used

- Apache Airflow: The primary orchestration tool for scheduling and managing the ETL workflow.
- Docker Compose: Provides a reproducible local Airflow environment with PostgreSQL.
- uv: Used to resolve, lock, and synchronize Python dependencies.
- Python: Used for scripting the data extraction and transformation logic.
- Bash: Utilized via Airflow's BashOperator to execute shell commands for tasks like unzipping and data manipulation.

## Data contract

The input archive is expected to contain three source files. The extraction stage keeps the selected fields in source order and consolidates them into one comma-separated row:

| Source | Format and selected positions | Normalized fields |
| --- | --- | --- |
| `vehicle-data.csv` | Comma-separated fields 1–4 | `vehicle_id`, `vehicle_type`, `vehicle_number`, `tollplaza_id` |
| `tollplaza-data.tsv` | Tab-separated fields 5–7 | `number_of_axles`, `tollplaza_id`, `tollplaza_code` |
| `payment-data.txt` | Fixed-width characters 1–10 and 11–20 | `payment_type_code`, `vehicle_code` |

Fixed-width positions are one-based and inclusive. The normalized output is therefore nine fields per source row: four CSV fields, three TSV fields, and two payment fields. The archive is expected to keep corresponding records aligned by row for the consolidation step. The DAG checks that all three extracted files have the same number of rows, then rejects empty consolidated output and rows that do not contain exactly nine fields.

The pipeline uppercases `vehicle_type`. Numeric rounding is not part of the source-file contract because the selected source fields do not define `vehicle_count` or `toll_amount`; any future numeric transformation must first add an explicit schema mapping and tests.

Supported scope is the unquoted archive format described above. The shell-based extractors do not support general CSV quoting, embedded commas, or embedded newlines; use a CSV-aware parser before expanding the input contract.

The intermediate transformed file is written to `airflow/dags/staging/transformed_data.csv`. The load stage validates that file and copies it to the final staging output at `airflow/dags/staging/final/transformed_data.csv`.

Each Airflow run extracts into its own temporary work directory. At the start of a run, only generated intermediate files and the project staging directory are removed; the downloaded archive at `airflow/dags/data/tolldata.tgz` is preserved.

## Pipeline

The Apache Airflow Directed Acyclic Graph (DAG) runs the three extractors in parallel after validating the input archive.

### Preparation

- Define DAG defaults, schedule, retry behavior, and concurrency limits.
- Extract the raw archive into a run-specific temporary directory.
- Validate that all required source files exist and are non-empty.

### Extract

This phase extracts three source formats into normalized intermediate files.

- Extract fields 1–4 from `vehicle-data.csv` into `data/csv_data.csv`.
- Extract fields 5–7 from `tollplaza-data.tsv` into `data/tsv_data.csv`.
- Extract fields 1–10 and 11–20 from `payment-data.txt` into `data/fixed_width_data.csv`.
- Consolidate the extracted files into `data/extracted_data.csv`.
- Validate that the consolidated output is non-empty and has nine fields per row.

### Transform

- Uppercase the `vehicle_type` field.
- Validate that the transformed output is non-empty, has nine fields per row, and contains an uppercase `vehicle_type`.

### Load

- Copy the validated transformed data into the final staging area.

### Task flow

The DAG's task pipeline defines the flow of the ETL process, ensuring that tasks are executed in the correct order. The flow is as follows:

```text
unzip_data -> validate_input_data -> [extract_data_from_csv, extract_data_from_tsv, extract_data_from_fixed_width] -> consolidate_data -> validate_consolidated_data -> transform_data -> validate_transformed_data -> load_data
```

## Operations

- Prepare data: Run `make extract-data`. Override `DATA_URL`, `DATA_DIR`, or `DATA_ARCHIVE` when using a different source archive. Set `DATA_SHA256=<checksum>` with `make get-data` to verify the downloaded archive.
- Create the environment: Run `make sync`. This uses the committed `uv.lock` file to create or synchronize `.venv`.
- Configure Compose: Copy `.env.example` to `.env` and change the local admin username and API JWT secret if needed. The checked-in default secret is for local development only.
- Initialize Airflow: Run `make compose-init` to create the metadata database.
- Start Airflow: Run `make compose-up`, then open `http://localhost:8080`. Airflow 3 generates the simple-auth password on first start; read it with `docker compose logs airflow-api-server`.
- Confirm DAG availability: The Compose services mount `airflow/dags` into the Airflow containers automatically.
- Enable and trigger: Access the Airflow UI, unpause the `ETL_toll_data` DAG, and manually trigger its execution.
- Scheduling: The DAG runs daily, does not backfill historical dates when it is unpaused, and allows only one active run at a time.
- Validate locally: Run `make check` to run the automated tests and parse the DAG without requiring a live Airflow scheduler.
- Monitor the DAG: Use the Airflow UI to monitor the progress of each task in the graphical view.
- Inspect tasks: Use the Airflow CLI command to list all tasks associated with the DAG.
- Stop Airflow: Run `make compose-down` to stop the services while preserving the PostgreSQL volume.

### Troubleshooting

- If the archive is missing, run `make extract-data` or provide a local `DATA_URL`/`DATA_ARCHIVE`.
- If `make check` fails, fix the reported test or DAG validation error before running the DAG in Airflow.
- If Airflow cannot import the DAG, confirm that the Compose services are running and that `airflow/dags/ETL_toll_data.py` exists on the host.
- If the UI port is busy, set `AIRFLOW_API_PORT` in `.env` and open the corresponding port instead.
- If a clean local reset is needed, run `docker compose down --volumes` to remove the PostgreSQL metadata and Airflow home volumes, then repeat `make compose-init`. This removes local Airflow history and the generated login password.

Airflow 3.0.6 supports Python 3.9–3.12. The project metadata enforces that supported range; use a compatible interpreter when running `make sync`.
