from datetime import datetime
from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
import json

# DAG mensile
with DAG(
    dag_id='mlops_ci_cd_train_monthly',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@monthly',  # Gira il primo giorno del mese a mezzanotte
    catchup=False,
    tags=['mlops', 'ci-cd'],
) as dag:

    # Task che chiama le API di GitHub per fare il trigger del workflow
    trigger_github_workflow = HttpOperator(
        task_id='trigger_github_ci_cd_train',
        http_conn_id='github_api',  # Dovrai configurare questa connessione nella UI di Airflow
        endpoint='repos/francescofrigerio/IL_TUO_REPO/actions/workflows/cicd-train-pipeline.yml/dispatches',
        method='POST',
        # Inviamo il body richiesto da GitHub per l'evento workflow_dispatch
        data=json.dumps({
            "ref": "main"  # Il branch da cui far partire il workflow
        }),
        headers={
            "Authorization": "Bearer {{ conn.github_api.password }}", # Recupera il Token da Airflow
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        response_check=lambda response: response.status_code == 204, # GitHub risponde con 204 No Content
    )

    trigger_github_workflow