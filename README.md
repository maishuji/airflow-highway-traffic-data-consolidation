# Highway Traffic Data Consolidation: An ETL Pipeline with Apache Airflow
## Project Overview

This project implements an Extract, Transform, and Load (ETL) pipeline using Apache Airflow. The goal is to address highway congestion by consolidating road traffic data from different toll plazas. The challenge lies in the diverse data formats used by various toll operators, including CSV, TSV, and fixed-width files. The pipeline is designed to collect data from these disparate sources, transform it into a standardized format, and load it into a staging area for further analysis.

### Technologies Used

- Apache Airflow: The primary orchestration tool for scheduling and managing the ETL workflow.
- Python: Used for scripting the data extraction and transformation logic.
- Bash: Utilized via Airflow's BashOperator to execute shell commands for tasks like unzipping and data manipulation.

### Data contract

The input archive is expected to contain three source files. The extraction stage keeps the selected fields in source order and consolidates them into one comma-separated row:

| Source | Format and selected positions | Normalized fields |
| --- | --- | --- |
| `vehicle-data.csv` | Comma-separated fields 1–4 | `vehicle_id`, `vehicle_type`, `vehicle_number`, `tollplaza_id` |
| `tollplaza-data.tsv` | Tab-separated fields 5–7 | `number_of_axles`, `tollplaza_id`, `tollplaza_code` |
| `payment-data.txt` | Fixed-width characters 1–10 and 11–20 | `payment_type_code`, `vehicle_code` |

Fixed-width positions are one-based and inclusive. The normalized output is therefore nine fields per source row: four CSV fields, three TSV fields, and two payment fields. The fixture is expected to keep corresponding records aligned by row for the consolidation step. The DAG checks that all three extracted files have the same number of rows, then rejects empty consolidated output and rows that do not contain exactly nine fields.

The transformation contract for this assignment is to uppercase `vehicle_type`. Numeric rounding is not part of the source-file contract because the selected source fields do not define `vehicle_count` or `toll_amount`; any future numeric transformation must first add an explicit schema mapping and tests.

The intermediate transformed file is written to `airflow/dags/staging/transformed_data.csv`. The load stage validates that file and copies it to the final staging output at `airflow/dags/staging/final/transformed_data.csv`.

Each Airflow run extracts into its own temporary work directory. At the start of a run, only generated intermediate files and the project staging directory are removed; the downloaded archive at `airflow/dags/data/tolldata.tgz` is preserved.

### ETL Pipeline Tasks

The Apache Airflow Directed Acyclic Graph (DAG) for this project is structured to perform the following tasks, with the three extractors running in parallel after input validation.
#### 1. Preparation

- Task 1.1: Define a set of default arguments for the DAG, including the owner, start date, and retry settings.
- Task 1.2: Instantiate the DAG with a unique ID and schedule.
- Task 2.1: Unzip the raw data archive to prepare the source files for extraction.
- Task 2.1.1: Validate that all required source files exist and are non-empty.

#### 2. Extract

This phase involves extracting data from three different file formats into a single, temporary file.

- Task 2.2: Extract fields 1–4 from `vehicle-data.csv` into `data/csv_data.csv`.
- Task 2.3: Extract fields 5–7 from `tollplaza-data.tsv` into `data/tsv_data.csv`.
- Task 2.4: Extract data from a fixed-width file (payment-data.txt).
- Task 2.5: Consolidate the extracted files into `data/extracted_data.csv`.
- Task 2.5.1: Validate that the consolidated output is non-empty and has nine fields per row.

#### 3. Transform

- Task 2.6: Transform the consolidated data by uppercasing the `vehicle_type` field.
- Task 2.6.1: Validate that the transformed output is non-empty, has nine fields per row, and contains an uppercase `vehicle_type`.

#### 4. Load

- Task 2.7: Load the transformed data into the final staging area.

### Task Pipeline Definition

The DAG's task pipeline defines the flow of the ETL process, ensuring that tasks are executed in the correct order. The flow is as follows:

unzip_data -> validate_input_data -> [extract_data_from_csv, extract_data_from_tsv, extract_data_from_fixed_width] -> consolidate_data -> validate_consolidated_data -> transform_data -> validate_transformed_data -> load_data
### How to Run the Project

- Prepare data: Run `make extract-data`. Override `DATA_URL`, `DATA_DIR`, or `DATA_ARCHIVE` when using a different source or local fixture. Set `DATA_SHA256=<checksum>` with `make get-data` to verify the downloaded archive.
- Submit the DAG: Copy the Python DAG file to the Airflow dags directory.
- Unpause and Trigger: Access the Airflow UI, unpause the new DAG, and manually trigger its execution.
- Scheduling: The DAG runs daily, does not backfill historical dates when it is unpaused, and allows only one active run at a time.
- Validate locally: Run `make test` to check the DAG structure without requiring a live Airflow scheduler.
- Monitor the DAG: Use the Airflow UI to monitor the progress of the DAG, observing the status of each task in - the graphical view.
- List Tasks: Use the Airflow CLI command to list all tasks associated with the DAG.

## Grading Criteria

This project is graded out of 25 points based on the following tasks:

### Exercise 1: Create imports, DAG argument and definition (4pts)

- Task 1.1: Define DAG arguments (2pts)
- Task 1.2: Define the DAG (2pts)

### Exercise 2: Create the tasks using BashOperator (13pts)

- Task 2.1: Create a task to unzip data (2pts)
- Task 2.2: Create a task to extract data from a CSV file (2pts)
- Task 2.3: Create a task to extract data from a TSV file (2pts)
- Task 2.4: Create a task to extract data from a fixed-width file (2pts)
- Task 2.5: Create a task to consolidate data (2pts)
- Task 2.6: Transform the data (2pts)
- Task 2.7: Define the task pipeline (1pt)

### Exercise 3: Getting the DAG operational (8pts)

- Task 3.1: Submit the DAG (1pt)
- Task 3.2: Unpause and trigger the DAG (3pts)
- Task 3.3: List the DAG tasks (2pts)
- Task 3.4: Monitor the DAG (2pts)

### Submission

Screenshots of the completed tasks in the Airflow UI and CLI will be submitted for peer review.
