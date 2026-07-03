import json
import requests
from datetime import datetime
import pendulum  

# 1. Import Core di Airflow
from airflow import DAG
from airflow.sdk import Param   
from airflow.models import Connection
from airflow.sdk.exceptions import AirflowFailException

# 2. Import degli Operatori Standard e Python
from airflow.providers.standard.operators.python import PythonOperator                                            
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator 

# 3. Import del pacchetto HTTP (Tutti uniti qui, senza duplicati!)
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
# from airflow.providers.http.hooks.http_hook import HttpHook
from airflow.providers.http.hooks.http import HttpHook

# Definisce il fuso orario italiano
local_tz = pendulum.timezone("Europe/Rome")

# con 0.8 ad ogni esecuzione
# partirebbe il train per cui 
# con le prestazioni attuali è meglio 0.7
TRESHOLD_VALUE = 0.7
TRAINING_DAG_ID = 'mlops_ci_cd_train_monthly'

def check_training_concurrency(**kwargs):
    """
    Controlla se il DAG di training è già in esecuzione.
    """
    try:
        hook = HttpHook(method='GET', http_conn_id='airflow_api_internal')
        response = hook.run(f'api/v1/dags/{TRAINING_DAG_ID}/dagRuns?state=running')
        data = response.json()
        active_runs = data.get('dag_runs', [])
        
        if active_runs:
            raise AirflowFailException(f"DAG '{TRAINING_DAG_ID}' già in esecuzione.")
        print(f"Nessun addestramento in corso. Procedo.")
    except AirflowFailException:
        raise
    except Exception as e:
        print(f"Impossibile interrogare l'API interna ({e}). Fallback sicuro...")

def check_model_metrics_from_github(**kwargs):
    """
    Questo task viene eseguito SOLO DOPO che l'HttpSensor ha confermato 
    che il file su GitHub esiste ed è pronto. 
    """
    url_file = "monitoring/latest_metrics.json"
    url = f"https://raw.githubusercontent.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/main/{url_file}"
    
    conn = Connection.get_connection_from_secrets('github_api')
    token = conn.password
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise AirflowFailException(f"Errore nel recupero metriche: {response.status_code}")
    
    data_list = response.json()
    if not data_list:
        raise AirflowFailException("Il file JSON è vuoto!")

    metrics = data_list[0]
    current_accuracy = float(metrics.get("accuracy", 0))
    
    print(f"Ultima Accuracy estratta = {current_accuracy}")
    
    if current_accuracy < TRESHOLD_VALUE:
        print(f"RETRAIN NECESSARIO: {current_accuracy} < {TRESHOLD_VALUE}")
        # Solleviamo un'eccezione esplicita per contrassegnare il task come FAILED
        raise AirflowFailException(f"Accuratezza sotto la soglia: {current_accuracy}")
        
    print("Monitoraggio superato. Il modello è stabile.")

GIORNO=1
MESE=6

# Per evitare bche airflow alla prima esecuzione
# lanci due volte il dag
default_args = {
    'owner': 'airflow',
}

with DAG(
    dag_id='mlops_metrics_monitoring_daily',
    default_args=default_args,
    start_date=datetime(2026, MESE, GIORNO, tzinfo=local_tz),
    # ogni giorno alle 9 di mattina
    # formato cron m h g m y 
    schedule='0 10 * * *', 
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

    # TASK 1: Controlla che non ci sia già attivo un training
    check_training = PythonOperator(
        task_id='check_training_running',
        python_callable=check_training_concurrency,
    )

    # TASK 2: lancia il workflow che genera i grafici e aggiorna il DB
    # trigger_github_monitoring = HttpOperator(
    #     task_id='trigger_github_monitoring_metrics',
    #    http_conn_id='github_api',  
    #    endpoint='repos/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/monitoring-metrics.yml/dispatches',
    #    method='POST',
        # Inv  il body richiesto da GitHub per l'evento workflow_dispatch
        # rende dinamico il body usando {{ params.execution_mode }}
    #    data=json.dumps({   "ref": "main",
    #                        "inputs": {
    #                            "mode": "{{ params.execution_mode }}"
    #                        }
    #                    }),
    #    headers={
    #        "Authorization": "Bearer {{ conn.github_api.password }}", 
    #        "Accept": "application/vnd.github+json",
    #        "X-GitHub-Api-Version": "2022-11-28"
    #    },
    #    response_check=lambda response: response.status_code == 204, 
    # )
    # TASK 2: Trigger del workflow GitHub (Asincrono, non aspetta il completamento)
    trigger_github_monitoring = HttpOperator(
        task_id='trigger_github_monitoring_metrics',
        http_conn_id='github_api',  
        endpoint='repos/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/monitoring-metrics.yml/dispatches',
        method='POST',
        data=json.dumps({
            "ref": "main",
            "inputs": {"mode": "{{ params.execution_mode }}"}
        }),
        headers={
            "Authorization": "Bearer {{ conn.github_api.password }}", 
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        response_check=lambda response: response.status_code == 204, 
    )

    # TASK 3 (ASINCRONO): Il sensore monitora l'URL finché non risponde 200 OK
    # non consuma risorse fisse del worker (modalità poke/reschedule) come lo sleep
    wait_for_github_file = HttpSensor(
        task_id='wait_for_github_metrics_file',
        http_conn_id='github_api',
        endpoint='repos/francescofrigerio/profai_10_mlops_prj_machineinnovation/contents/monitoring/latest_metrics.json',
        method='GET',
        headers={
            "Authorization": "Bearer {{ conn.github_api.password }}",
            "Accept": "application/vnd.github+json"
        },
        response_check=lambda response: response.status_code == 200,
        poke_interval=30,  # Controlla ogni 30 secondi
        timeout=300,       # Timeout massimo 5 minuti
        mode='reschedule'  # Rilascia il worker tra un controllo e l'altro 
    )

    # TASK 4: verifica effetiva della soglia di accuratezza, legge il file JSON da GitHub
    verify_metrics_threshold = PythonOperator( task_id='verify_metrics_threshold',
                                                python_callable=check_model_metrics_from_github,
                                             )

    # TASK 5: Scatta SOLO se il TASK 4 fallisce (trigger_rule='one_failed')
    # quindi solo se l'accuracy è sotto la soglia
    trigger_emergency_retrain = TriggerDagRunOperator( task_id='trigger_emergency_retrain', 
                                            trigger_dag_id=TRAINING_DAG_ID,
                                            trigger_rule='one_failed',                
                                            # Gira solo se verify_metrics_threshold va in ERRORE
                                            conf={"reason": "Automatic trigger due to performance drop under 0.80"},
                                            )

    # trigger_github_monitoring >> verify_metrics_threshold >> trigger_emergency_retrain
    # check_training >> trigger_github_monitoring >> verify_metrics_threshold
    # Il trigger di emergenza dipende DIRETTAMENTE e SOLO dal task di verifica metriche
    # verify_metrics_threshold >> trigger_emergency_retrain

    # 
    # Ecco come funziona logicamente il flusso MLOps:
    # trigger_github_monitoring (HttpOperator): Dice a GitHub "Fai partire il workflow". 
    # Riceve un codice 204 (OK, ho recepito l'ordine) e termina immediatamente. 
    # Non sa quando il workflow su GitHub finirà davvero.
    # wait_for_github_file (HttpSensor): Entra in gioco subito dopo. 
    # Invece di far fermare tutto il codice con un pesante time.sleep(180),
    # usato nelle prime versioni del codice 
    # questo sensore fa una chiamata HTTP veloce a GitHub ogni 30 secondi 
    # (poke_interval=30) chiedendo: 
    # "C'è il file JSON aggiornato?".
    # Se GitHub risponde 404 (il file non c'è ancora o si sta aggiornando), 
    # il sensore si "addormenta" (mode='reschedule') liberando la CPU del tuo Codespace.
    # Dopo 30 secondi ci riprova. 
    # Appena riceve 200 (File pronto!), 
    # il task diventa verde e passa la palla al punto successivo.
    # verify_metrics_threshold (PythonOperator): 
    # Legge finalmente il contenuto del file JSON, sicuro al 100% 
    # che il file esista e sia aggiornato, confrontando l'accuratezza.
    check_training >> trigger_github_monitoring >> wait_for_github_file >> verify_metrics_threshold >> trigger_emergency_retrain

