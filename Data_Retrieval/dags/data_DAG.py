from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'nate',
    'depends_on_past': False,
    'start_date': datetime(2020, 4, 5),
    'email': ['nate.salima@outlook.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'schedule_interval': '@daily',
}

dag = DAG('datafile', default_args=default_args)

t1 = BashOperator(
    task_id='strava_s3',
    bash_command='python3 ~/strava_s3.py',
    dag=dag)

t2 = BashOperator(
    task_id='s3_redshift',
    bash_command='python3 ~/s3_redshift.py',
    dag=dag)

t3 = BashOperator(
    task_id='s3_dynamodb',
    bash_command='python3 ~/s3_dynamodb.py',
    dag=dag)

t1 >> t3
t1 >> t2