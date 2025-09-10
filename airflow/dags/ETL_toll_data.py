# Import the required packages
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Define the default DAG arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1), # Using a fixed date for idempotency
    'email': 'airflow@example.com',
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG with a descriptive ID
dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    description='A DAG for ETL processing of toll data',
    schedule_interval=timedelta(days=1), # Run once every day
)

unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command='tar -xvzf ./tolldata.tgz -C ./data/',
    dag=dag,
)

extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command='cut -d"," -f1,2,3,4 '
                 './data/vehicle-data.csv '
                 '> ./data/csv_data.csv',
    dag=dag,
)

extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command='cut -f5,6,7 '
                 './data/tollplaza-data.tsv '
                 '> ./data/tsv_data.csv',
    dag=dag,
)
