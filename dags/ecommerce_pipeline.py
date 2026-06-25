from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'disney',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_pipeline',
    default_args=default_args,
    description='E-commerce data warehouse pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ecommerce', 'dbt', 'warehouse'],
) as dag:

    generate_data = BashOperator(
        task_id='generate_data',
        bash_command='cd /usr/local/ecommerce_dw && python src/generate_data.py',
    )

    dbt_staging = BashOperator(
        task_id='dbt_staging',
        bash_command='cd /usr/local/ecommerce_dw/ecommerce_dbt && dbt run --select staging',
    )

    dbt_dimensions = BashOperator(
        task_id='dbt_dimensions',
        bash_command='cd /usr/local/ecommerce_dw/ecommerce_dbt && dbt run --select dimensions',
    )

    dbt_facts = BashOperator(
        task_id='dbt_facts',
        bash_command='cd /usr/local/ecommerce_dw/ecommerce_dbt && dbt run --select facts',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /usr/local/ecommerce_dw/ecommerce_dbt && dbt test',
    )

    generate_data >> dbt_staging >> dbt_dimensions >> dbt_facts >> dbt_test