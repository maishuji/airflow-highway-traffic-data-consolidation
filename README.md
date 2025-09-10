# Highway Traffic Data Consolidation: An ETL Pipeline with Apache Airflow
## Project Overview

This project implements an Extract, Transform, and Load (ETL) pipeline using Apache Airflow. The goal is to address highway congestion by consolidating road traffic data from different toll plazas. The challenge lies in the diverse data formats used by various toll operators, including CSV, TSV, and fixed-width files. The pipeline is designed to collect data from these disparate sources, transform it into a standardized format, and load it into a staging area for further analysis.
### Technologies Used

- Apache Airflow: The primary orchestration tool for scheduling and managing the ETL workflow.
- Python: Used for scripting the data extraction and transformation logic.
- Bash: Utilized via Airflow's BashOperator to execute shell commands for tasks like unzipping and data manipulation.

### ETL Pipeline Tasks

The Apache Airflow Directed Acyclic Graph (DAG) for this project is structured to perform the following tasks sequentially.
#### 1. Preparation

- Task 1.1: Define a set of default arguments for the DAG, including the owner, start date, and retry settings.
- Task 1.2: Instantiate the DAG with a unique ID and schedule.
- Task 2.1: Unzip the raw data archive to prepare the source files for extraction.

#### 2. Extract

This phase involves extracting data from three different file formats into a single, temporary file.

- Task 2.2: Extract data from the tolldata.csv file.
- Task 2.3: Extract data from the tollplaza_data.tsv file.
- Task 2.4: Extract data from a fixed-width file (payment-data.txt).
- Task 2.5: Consolidate the data extracted from the CSV, TSV, and fixed-width files into a single extracted_data.txt file.

#### 3. Transform

- Task 2.6: Transform the consolidated data by rounding the vehicle_count and toll_amount values to the nearest integer.

#### 4. Load

- Task 2.7: Load the transformed data into the final staging area.

### Task Pipeline Definition

The DAG's task pipeline defines the flow of the ETL process, ensuring that tasks are executed in the correct order. The flow is as follows:

unzip_data_task -> extract_from_csv -> extract_from_tsv -> extract_from_fixed_width -> consolidate_data_task -> transform_data_task -> load_data_task
### How to Run the Project

- Submit the DAG: Copy the Python DAG file to the Airflow dags directory.
- Unpause and Trigger: Access the Airflow UI, unpause the new DAG, and manually trigger its execution.
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