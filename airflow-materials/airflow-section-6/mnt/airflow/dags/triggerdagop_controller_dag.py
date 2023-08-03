import pprint as pp
import airflow.utils.dates
from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
        "owner": "airflow", 
        "start_date": airflow.utils.dates.days_ago(1)
    }

'''
#A new parameter called “dag_run_object”.This parameter is automatically given by the TriggerDagRunOperator and it corresponds to a simple
# class composed by a run_id and a payload.The payload allows you to send data from the controller DAG to the target DAG.
# That's what you can see here.A dictionary with a key value pair message having the value given from the params “Hi from the controller” is assigned to the payload attribute.
'''
def conditionally_trigger(context, dag_run_obj):
    if context['params']['condition_param']:
        dag_run_obj.payload = {
                'message': context['params']['message']
            }
        pp.pprint(dag_run_obj.payload)
        return dag_run_obj

with DAG(dag_id="triggerdagop_controller_dag", default_args=default_args, schedule_interval="@once") as dag:
    trigger = TriggerDagRunOperator(
        task_id="trigger_dag",
        trigger_dag_id="triggerdagop_target_dag",
        provide_context=True,
        python_callable=conditionally_trigger,
        params={
            'condition_param': True, 
            'message': 'Hi from the controller'
        },
    )

    last_task = DummyOperator(task_id="last_task")

    trigger >> last_task