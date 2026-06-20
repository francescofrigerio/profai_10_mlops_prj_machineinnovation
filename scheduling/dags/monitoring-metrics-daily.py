import json
import time
import requests  # per leggere il file da GitHub

from datetime import datetime
import pendulum  

from airflow import DAG
from airflow.models.param import Param
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator  
from airflow.models import Connection                              

# Definisce il fuso orario italiano
local_tz = pendulum.timezone("Europe/Rome")

def check_model_metrics_from_github():
   
    # diamo tempo al workflow su github di girare e scrivere il file
    # altrimenti corriamo il rischio di avere dati vecchi.
    print("In attesa che GitHub Actions completi la generazione del JSON...")
    time.sleep(180)

    url_file = "monitoring/latest_metrics.json"
    url = "https://raw.githubusercontent.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/main/" + url_file
    
    # Non funziona qui usare il Token di autenticazione
    # headers = {"Authorization": "Bearer {{ conn.github_api.password }}"}
    conn = Connection.get_connection_from_secrets('github_api')
    token = conn.password
    # pwd nella richiesta di requests usando la f-string di Python
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Impossibile recuperare le metriche da GitHub. Status code: {response.status_code}")
    
    # Leggiamo il valore (es. assumendo che il file sia un JSON tipo: {"accuracy": 0.84})
    data_list = response.json()
    if not data_list:
        raise ValueError("Il file JSON delle metriche è vuoto!")

    metrics = data_list[0]
    current_accuracy = float(metrics.get("accuracy", 0))
    
    print(f"Monitoraggio : Ultima Accuracy estratta dal database = {current_accuracy}")
    
    soglia_minima = 0.70
    if current_accuracy < soglia_minima:
        print(f"RETRAIN NECESSARIO: L'accuratezza ({current_accuracy}) è inferiore a {soglia_minima}")
        raise ValueError(f"L'accuratezza è crollata a {current_accuracy}!")
        
    print("Monitoraggio superato. Il modello è stabile.")

with DAG(
    dag_id='mlops_metrics_monitoring_daily',
    start_date=datetime(2026, 1, 1, tzinfo=local_tz),
    # ogni giorno alle 9 di mattina
    # formato cron m h g m y 
    schedule='0 9 * * *', 
    catchup=False,
    tags=['mlops', 'monitoring'],
    # Definisce il parametro che appare sulla UI di Airflow
   params={
        "execution_mode": Param(
            default="demo", 
            # default="prod",
            type="string", 
            enum=["demo", "prod"], 
            description="Seleziona la modalità di esecuzione per GitHub Actions"
        )
    },
) as dag:

    # TASK 1: Resta invariato, lancia il workflow che genera i grafici e aggiorna il DB
    trigger_grafana_monitoring = HttpOperator(
        task_id='trigger_github_monitoring_metrics',
        http_conn_id='github_api',  
        endpoint='repos/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/monitoring-metrics.yml/dispatches',
        method='POST',
        # Inv  il body richiesto da GitHub per l'evento workflow_dispatch
        # rende dinamico il body usando {{ params.execution_mode }}
        data=json.dumps({   "ref": "main",
                            "inputs": {
                                "mode": "{{ params.execution_mode }}"
                            }
                        }),
        headers={
            "Authorization": "Bearer {{ conn.github_api.password }}", 
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        response_check=lambda response: response.status_code == 204, 
    )

    # TASK 2: Ora legge il valore VERO aggiornato dal Task 1
    verify_metrics_threshold = PythonOperator( task_id='verify_metrics_threshold',
                                                python_callable=check_model_metrics_from_github,
                                             )

    # TASK 3: Scatta SOLO se il TASK 2 fallisce (trigger_rule='one_failed')
    trigger_emergency_retrain = TriggerDagRunOperator( task_id='trigger_emergency_retrain',
                                            trigger_dag_id='mlops_ci_cd_train_monthly',  
                                            trigger_rule='one_failed',                
                                            # Gira solo se verify_metrics_threshold va in ERRORE
                                            conf={"reason": "Automatic trigger due to performance drop under 0.80"},
                                            )

    trigger_grafana_monitoring >> verify_metrics_threshold >> trigger_emergency_retrain