from datetime import datetime
from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
import json
import requests  # Utilizziamo requests per leggere il file da GitHub

def check_model_metrics_from_github():
    # URL del file raw su GitHub (sostituisci con il percorso corretto del tuo file di metriche txt/json)
    # Esempio: se il file si chiama 'latest_metrics.json' nella cartella monitoring
    url = "https://raw.githubusercontent.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/main/monitoring/latest_metrics.json"
    
    # Recuperiamo il file usando il Token di autenticazione
    headers = {"Authorization": "Bearer {{ conn.github_api.password }}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Impossibile recuperare le metriche da GitHub. Status code: {response.status_code}")
    
    # Leggiamo il valore (es. assumendo che il file sia un JSON tipo: {"accuracy": 0.84})
    data = response.json()
    current_accuracy = float(data.get("accuracy", 0))
    
    print(f"Monitoraggio Reale: Accuratezza estratta dal database = {current_accuracy}")
    
    soglia_minima = 0.80
    if current_accuracy < soglia_minima:
        print(f"RETRAIN NECESSARIO: L'accuratezza ({current_accuracy}) è inferiore a {soglia_minima}")
        raise ValueError(f"L'accuratezza è crollata a {current_accuracy}!")
        
    print("Monitoraggio superato. Il modello è stabile.")

with DAG(
    dag_id='mlops_metrics_monitoring_daily',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['mlops', 'monitoring'],
) as dag:

    # TASK 1: Resta invariato, lancia il workflow che genera i grafici e aggiorna il DB
    trigger_grafana_monitoring = HttpOperator(
        task_id='trigger_github_monitoring_metrics',
        http_conn_id='github_api',  
        endpoint='repos/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/monitoring-metrics.yml/dispatches',
        method='POST',
        data=json.dumps({"ref": "main"}),
        headers={
            "Authorization": "Bearer {{ conn.github_api.password }}", 
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        response_check=lambda response: response.status_code == 204, 
    )

    # TASK 2: Ora legge il valore VERO aggiornato dal Task 1
    verify_metrics_threshold = PythonOperator(
        task_id='verify_metrics_threshold',
        python_callable=check_model_metrics_from_github,
    )

    trigger_grafana_monitoring >> verify_metrics_threshold