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

create-venv:
	python3 -m venv ./venv && \
	./venv/bin/python3 -m pip install --upgrade pip && \
	./venv/bin/python3 -m pip install -r requirements.txt

test:
	python3 -m unittest discover -s tests -p 'test_*.py'
