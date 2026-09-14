DATA_URL ?= https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz
DATA_DIR ?= ./airflow/dags/data
DATA_ARCHIVE ?= $(DATA_DIR)/tolldata.tgz
DATA_SHA256 ?=

get-data:
	mkdir -p "$(DATA_DIR)"
	wget --no-verbose --output-document="$(DATA_ARCHIVE)" "$(DATA_URL)"
	if [ -n "$(DATA_SHA256)" ]; then \
		printf '%s  %s\n' "$(DATA_SHA256)" "$(DATA_ARCHIVE)" | sha256sum --check --status -; \
	fi
	
extract-data: get-data
	tar -xvzf "$(DATA_ARCHIVE)" -C "$(DATA_DIR)"

sync:
	uv sync --locked

test:
	uv run --locked python -m unittest discover -s tests -p 'test_*.py'

check: test
	uv run --locked python -c 'import ast; from pathlib import Path; ast.parse(Path("airflow/dags/ETL_toll_data.py").read_text(encoding="utf-8")); print("DAG syntax: OK")'

compose-config:
	docker compose config --quiet

compose-init: compose-config
	mkdir -p airflow/logs airflow/plugins
	docker compose up airflow-init

compose-up: compose-init
	docker compose up -d

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f airflow-api-server
