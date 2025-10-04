## How to reset the password ( airflow 3.x.x)
If you need to reset the default admin password for your Airflow instance, follow these steps:

```
# 1. Set your Airflow home directory
export AIRFLOW_HOME=<your_airflow_home>

# 2. Reset the Airflow metadata database
airflow db reset -y

# 3. Remove the old auto-generated admin password file
rm -f "$AIRFLOW_HOME/standalone_admin_password.txt"

# 4. Start Airflow in standalone mode (a new password will be generated)
airflow standalone
```

After running airflow standalone, check the console output for the new admin username and password.
You can also find them in the newly created file:

```
$AIRFLOW_HOME/standalone_admin_password.txt
```