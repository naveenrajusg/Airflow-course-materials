from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2023, 6, 28),
    'owner': 'Airflow',
    'email': 'owner@test.com'
}




with DAG(dag_id='pool_dag', schedule_interval='0 0 * * *', default_args=default_args, catchup=False) as dag:
    
    # get forex rates of JPY and push them into XCOM
    get_forex_rate_EUR = SimpleHttpOperator(
        task_id='get_forex_rate_EUR',
        method='GET',
        http_conn_id='forex_api',
        pool='forex_api_pool',
        # endpoint='/latest?base=EUR',
        endpoint='api_forex_exchange_eur.json',
        priority_weight=1,
        xcom_push=True
    )



    # get forex rates of JPY and push them into XCOM
    get_forex_rate_USD = SimpleHttpOperator(
        task_id='get_forex_rate_USD',
        method='GET',
        http_conn_id='forex_api',
        pool='forex_api_pool',
        # endpoint='/latest?base=USD',
        endpoint='api_forex_exchange_usd.json',
        priority_weight=2,
        xcom_push=True
    )

    # In the code snippet you provided, xcom_push=True is a parameter of the SimpleHttpOperator task. XCom (short for Cross-Communication)
    # is a feature in Apache Airflow, a workflow management platform, that allows tasks to exchange small amounts of data. By setting xcom_push=True,
    # you are instructing the SimpleHttpOperator to push the result of the HTTP request to XCom.
    #
    # In this specific case, the result of the HTTP request is the forex rate for JPY (Japanese Yen) obtained from the specified API endpoint.
    # By pushing this result to XCom, it can be accessed by other tasks downstream in the workflow, allowing them to utilize the forex rate value
    # for further processing or analysis.

    # get forex rates of JPY and push them into XCOM
    get_forex_rate_JPY = SimpleHttpOperator(
        task_id='get_forex_rate_JPY',
        method='GET',
        http_conn_id='forex_api',
        pool='forex_api_pool',
        # endpoint='/latest?base=JPY',
        endpoint='api_forex_exchange_eur.json', #JPY endpoint was not available so reusing EUR endpoint
        priority_weight=3,
        xcom_push=True
    )


    # The bash_command you provided appears to be a template written in Jinja syntax. In Apache Airflow, the bash_command parameter in a BashOperator task allows you to
    # specify the shell command that will be executed when the task is triggered. In this case, the provided bash_command is using Jinja templating to dynamically generate
    # the shell commands based on the tasks in the DAG.
    #
    # Here's how the bash_command works:
    #
    # {% for task in dag.task_ids %}: This is the start of a for loop that iterates over the task_ids of the current DAG. It will loop through each task in the DAG.
    #
    # echo "{{ task }}": This line uses the echo command to print the name of the current task.
    #
    # echo "{{ ti.xcom_pull(task) }}": This line uses the echo command to print the result of pulling the XCom value associated with the current task. The ti.xcom_pull(task) function retrieves
    # the XCom value pushed by the task with the given task_id.
    #
    # {% endfor %}: This is the end of the for loop.
    #
    # When the BashOperator executes this bash_command, it will iterate over each task in the DAG, print the task name, and then print the associated XCom value (if any) using the ti.xcom_pull(task) function.

    # Templated command with macros
    bash_command="""
        {% for task in dag.task_ids %}
            echo "{{ task }}"
            echo "{{ ti.xcom_pull(task) }}"
        {% endfor %}
    """

    # we have a task named “show_data” that will fetch the rates stored from the metadata database of Airflow and will show them into the output.
    # Show rates
    show_data = BashOperator(
        task_id='show_result',
        bash_command=bash_command
    )

    [get_forex_rate_EUR, get_forex_rate_USD, get_forex_rate_JPY] >> show_data