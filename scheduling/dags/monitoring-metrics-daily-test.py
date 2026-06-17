from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import random  # Simuliamo il recupero delle metriche

def check_model_metrics():
    # query al DB di sqlite o chiamata a MLflow
    # Come esempio calcoliamo l'accuratezza attuale
    current_accuracy = random.uniform(0.75, 0.95)
    print(f"Monitoraggio del {datetime.now().date()}: Accuratezza attuale = {current_accuracy}")
    
    soglia_minima = 0.80
    
    if current_accuracy < soglia_minima:
        print(f"Accuratezza sotto la soglia ({soglia_minima}). Avvio RE-TRAIN.")
        raise ValueError(f"L'accuratezza ({current_accuracy}) è sotto la soglia di {soglia_minima}!")
        
    else:
        print("Metriche ottime. Nessuna azione necessaria.")
        

    print("Monitoraggio superato con successo.")

with DAG(
    dag_id='ml_metrics_monitoring_daily',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@daily',  # Gira ogni giorno a mezzanotte
    catchup=False,
    tags=['mlops', 'monitoring'],
) as dag:

    run_monitoring = PythonOperator(
        task_id='calculate_and_verify_metrics',
        python_callable=check_model_metrics,
    )

    run_monitoring