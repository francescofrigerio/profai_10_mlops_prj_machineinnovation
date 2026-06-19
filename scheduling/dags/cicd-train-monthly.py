from datetime import datetime
import pendulum 

from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.models.param import Param
import json

# Definisce il fuso orario italiano
local_tz = pendulum.timezone("Europe/Rome")

GIORNO=1
MESE=1

# DAG mensile
with DAG(
    dag_id='mlops_ci_cd_train_monthly',
    # start_date=datetime(2026, GIORNO, MESE),
    start_date=datetime(2026, GIORNO, MESE, tzinfo=local_tz),
    # Gira il 1° giorno di OGNI MESE a mezzanotte 
    # formato cron m h g m y
    schedule='0 0 1 * *',
    # schedule='30 8 1 * *',  
    catchup=False,
    tags=['mlops', 'ci-cd'],
    # Definisce il parametro che appare sulla UI di Airflow
    params={
        "execution_mode": Param(
            # default="demo", 
            default="prod",
            type="string", 
            enum=["demo", "prod"], 
            description="Seleziona la modalità di esecuzione per GitHub Actions"
        )
    },
) as dag:

    
    trigger_github_workflow = HttpOperator(
        task_id='trigger_github_ci_cd_train',
        http_conn_id='github_api',  # vedere configurazione connessione nella UI di Airflow
        endpoint='repos/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/cicd-train-pipeline.yml/dispatches',
        method='POST',
        # Inv  il body richiesto da GitHub per l'evento workflow_dispatch
        # rende dinamico il body usando {{ params.execution_mode }}
        data=json.dumps({ "ref": "main",
                            "inputs": {
                                "mode": "{{ params.execution_mode }}"
                            }
                        }),
        # qui non specifica nulla sul campo login
        # per cui deve essere lasciato vuoto su airflow
        headers={
            "Authorization": "Bearer {{ conn.github_api.password }}", # Recupera il Token da Airflow
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        response_check=lambda response: response.status_code == 204, # GitHub risponde con 204 No Content
    )

    trigger_github_workflow