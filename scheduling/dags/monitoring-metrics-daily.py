from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
import random

def check_model_metrics():
    current_accuracy = random.uniform(0.75, 0.95)
    print(f"Monitoraggio: Accuratezza attuale = {current_accuracy}")
    
    soglia_minima = 0.85
    
    # Invece di sollevare un errore, decidiamo quale strada (task) prendere
    if current_accuracy < soglia_minima:
        print(f"Accuratezza sotto la soglia ({soglia_minima}). Avvio RE-TRAIN.")
        return 'trigger_retrain_dag' # ID del task che avvia il train
    else:
        print("Metriche ottime. Nessuna azione necessaria.")
        return 'metrics_ok' # ID del task di successo (non fa nulla)

with DAG(
    dag_id='ml_metrics_monitoring_daily',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['mlops', 'monitoring'],
) as dag:

    # 1. Task che valuta le metriche e decide la strada da prendere
    verify_metrics = BranchPythonOperator(
        task_id='calculate_and_verify_metrics',
        python_callable=check_model_metrics,
    )

    # 2. Strada A: Se le metriche sono KO, questo task chiama il DAG mensile
    trigger_retrain = TriggerDagRunOperator(
        task_id='trigger_retrain_dag',
        trigger_dag_id='mlops_ci_cd_train_monthly', # Deve coincidere con il dag_id del file mensile
        wait_for_completion=False, # Airflow lancia il train e non aspetta che finisca, prosegue oltre
    )

    # 3. Strada B: Se le metriche sono OK, il DAG finisce qui senza fare nulla
    metrics_ok = EmptyOperator(
        task_id='metrics_ok'
    )

    # Definizione del flusso (bivio)
    verify_metrics >> [trigger_retrain, metrics_ok]