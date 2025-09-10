get-data:
	mkdir -p ./airflow/dags/data
	wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz
	tar -xvzf tolldata.tgz -C ./airflow/dags/data

create-venv:
	python3 -m venv ./venv && \
	./venv/bin/python3 -m pip install --upgrade pip && \
	./venv/bin/python3 -m pip install -r requirements.txt
