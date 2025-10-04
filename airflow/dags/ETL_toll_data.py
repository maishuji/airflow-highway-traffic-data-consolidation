# Import the required packages
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

DAGS_DIR = Path(__file__).resolve().parent

WORK_DIR = Path(tempfile.gettempdir()) / "etl_toll_data"

# Define the default DAG arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1), # Using a fixed date for idempotency
    # 'email': 'airflow@example.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG with a descriptive ID
dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    description='A DAG for ETL processing of toll data',
    schedule="@daily",  # Run once every day
)


unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command='set -euo pipefail; '
                 f'mkdir -p "{WORK_DIR}"; '
                 f'tar -xvzf ./data/tolldata.tgz -C {WORK_DIR}/',
    dag=dag,
    cwd=str(DAGS_DIR)
)

cur_dir = BashOperator(
    task_id='current_dir',
    bash_command='pwd >> log1.txt',
    dag=dag,
    cwd=str(DAGS_DIR)
)

extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command='cut -d"," -f1,2,3,4 '
                 f'{WORK_DIR}/vehicle-data.csv '
                 '> ./data/csv_data.csv',
    dag=dag,
    cwd=str(DAGS_DIR)
)

extract_data_from_tsv = BashOperator(
    task_id="extract_data_from_tsv",
    cwd=str(DAGS_DIR),
    bash_command=f"""
      set -euo pipefail
      # extract cols 5–7, turn tabs into commas
      cut -f5,6,7 {WORK_DIR}/tollplaza-data.tsv | tr '\\t' ',' > ./data/tsv_data.csv
      # normalize CRLF -> LF
      sed -i 's/\\r$//' ./data/tsv_data.csv
      echo "Wrote ./data/tsv_data.csv (normalized to LF)"
    """,
    dag=dag,
)


extract_data_from_fixed_width = BashOperator(
    task_id="extract_data_from_fixed_width",
    cwd=str(DAGS_DIR),  # run relative to your DAGs folder
    bash_command=f"""
      set -euo pipefail
      awk '{{print $(NF-1) "," $NF}}' {DAGS_DIR}/data/payment-data.txt \
        > {DAGS_DIR}/data/fixed_width_data.csv
      echo "Wrote {DAGS_DIR}/data/fixed_width_data.csv"
    """,
    dag=dag,
)

consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command='paste -d"," '
                 './data/csv_data.csv '
                 './data/tsv_data.csv '
                 './data/fixed_width_data.csv '
                 '> ./data/extracted_data.csv',
    dag=dag,
    cwd=str(DAGS_DIR)
)

transform_data = BashOperator(
    task_id="transform_data",
    cwd=str(DAGS_DIR),
    bash_command="""
      set -euo pipefail
      DATA_DIR=./data
      STAGING_DIR=./staging
      mkdir -p "$STAGING_DIR"s

      # uppercase the 4th field (vehicle_type)
      awk -F',' 'BEGIN{OFS=","} {$4=toupper($4); print}' "$DATA_DIR/extracted_data.csv" > "$STAGING_DIR/transformed_data.csv"

      echo "Wrote $STAGING_DIR/transformed_data.csv"
    """,
    dag=dag,
)


unzip_data >> [extract_data_from_csv, extract_data_from_tsv, extract_data_from_fixed_width] >> consolidate_data >> transform_data