                  
                  
                  # MACHINE INNOVATION SCHEDULAZIONE E ORCHESTRAZIONE

## 1. `08-scheduling.md`
Questo documento descrive la configurazione Machine Innovation su Airflow
per la schedulazione e l'orchestrazione del sistema.
In fondo si trovano anche accenni sull'installazione per sistemisti e sviluppatori.

## 2. Descrizione Schedulazione e Orchestrazione con Airflow

2.1 Task di schedulazione mensile per il retrain automatico 
, a patto che il modello non soffra 
di data drift ( improvvisi cambi repentini di trend di mercato). 

cco gli step eseguiti dal retraining automatico di Airflow
```mermaid
 [DAG Retrain Mensile]
          │
          ▼
   [Workflow Retrain]
          │
          ▼
      [sqlite.db]
          │
          ▼ 
     [HF Space]
```

2.2 Task di schedulazione per il monitoraggio continuo.
unita a un trigger automatico se il DAG di monitoraggio 
giornaliero rileva che le metriche di accuratezza sono scese sotto una certa soglia.

Ecco gli step eseguiti dal monitoraggio continuo di Airflow
```mermaid
   [STEP1: DAG Daily Monitoring]
          │
          ▼
  [Workflow Monitoring]
          │
          ▼
     [sqlite.db] 
          │
          ▼
   [latest_metrics.json]
          │
          ▼
[STEP2:DAG Daily Monitoring]
          │
          ├─ accuracy >= 0.80
          │      STOP
          │
          └─ accuracy < 0.80
                 │
                 ▼
          [Workflow Retrain]
```
.
STEP1: Lo script analizza il database SQLite con i dati reali raccolti da Hugging Face
e genera il file latest_metrics.json.

STEP2: Se le metriche scendono sotto la soglia critica (accuracy=0.80), Airflow intercetta 
il fallimento e attiva immediatamente il DAG di Retrain, 
senza aspettare la fine del mese.


## 3. Manutenzione del sistema
per fare pulizia sul disco e cancellare i vecchi container
```bash
docker system prune -a --volumes -f
```

## 4. AirFlow Setup
4.1. La script ./setup.sh --init script ha creato la cartella scheduling e le sotto directory.

Alcuni directories sono montate(comando mount) dal container il che significa
che il loro contenuto è sincronizzato tra il pc locale e il container.

./dags - dove mettere i file python dei singoli dag.
./logs - contiene i logs per l'escuzione dei task e la schedulazione.
./config - si possono aggiungere log parser custom oppure airflow_local_settings.py per configurare policy a livello cluster.
./plugins - serve per inserire custom plugins .


4.2. Eseguire i seguenti comandi per installare e inizializzare airflow.
```bash
cd scheduling
# download airflow
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.2.2/docker-compose.yaml'

# to remove previous installed version
docker compose down --volumes --remove-orphans # reset totale se non è la prima installazione
cd ..
# 1. (Opzionale) Attivi l'ambiente locale solo per l'editor di testo
source .venv/bin/activate
pip install apache-airflow  # Solo per far felice VS Code/PyCharm non è presente nel requirements

# 2. Inizializza il database di Airflow dentro Docker (Crea cartelle, utenti e log)
docker compose up airflow-init

# 3. Avvia Airflow vero e proprio (Webserver, Scheduler, Worker)
docker compose up -d

# 4. Stop
docker compose down

# 5. Test running state
docker ps
```

Dopo l'esecuzione controllare la visibilita della porta after 8080
Se non funziona aggiungere la seguente configurazione all'environment
nel file ./scheduling/docker-compose.yml

AIRFLOW__WEBSERVER__ENABLE_PROXY_FIX: 'True'
AIRFLOW__WEBSERVER__EXPOSE_CONFIG: 'True'
AIRFLOW__WEBSERVER__BASE_URL: 'https://turbo-space-fishstick-q47wggx66w63rg5-8080.app.github.dev'

Credenziali di default di airflow
login airflow 
password airflow

4.3. Creazione DAG (Directed Acyclic Graph)
Valgono le seguenti considerazioni prese dalla documentazione
per riepilogare il funzionamento dei dag.

D=Directed : 
The flow has a precise direction.
If task A must be performed before task B,
there is a link from A to B, never ambiguos.

A=Acyclic: 
Infinite cycles or loops are not allowed. The flow cannot backtrack;
if task B depends on A, A cannot depend on B.

G=Graph: 
A graph is a structure composed of nodes (the tasks) connected by edges (the dependencies).

A DAG doesn't compute , but organize execution. 
It's based upon Operators (Task) and Dependencies (Edge):: 

Operators (Task): a single Unit of work
There is some  Operators to run python (PythonOperator)
as script Bash (BashOperator), query SQL.

Dependencies (Edge): 
It's the narrow that links the task
with Airflow defines it with bitwise operators >>. 
For example : task_A >> task_B means "run B solo after A wa terminate with succesfull".

4.4 Installare le estensioni di docker nel codespac(CTRL+SHIFT+X)
```bash
# Command to reset the dag cache
cd ./scheduling/dag
find . -type d -name "__pycache__" -exec rm -rf {} +

# 4.5 Mancato accesso alla dashboard (airflow/airfloe)
# eseguire in ordine e riprovare ad accedere
cd scheduling/
docker compose down -v
docker system prune -f
docker compose up -d

# Controlli
docker compose ps

docker compose logs airflow-webserver
# KO no such service: airflow-webserver

sudo lsof -i :8080
# KO docker-pr 31538 root    8u  IPv4 1051593      0t0  TCP *:http-alt (LISTEN)
# KO docker-pr 31545 root    8u  IPv6 1051594      0t0  TCP *:http-alt (LISTEN)

# lista servizi disponibili
docker compose config --services

# Ferma tutti i container docker attivi sul sistema
docker kill $(docker ps -q)

# 1. Forza lo spegnimento di qualsiasi container attivo in questo ambiente
docker rm -f $(docker ps -aq)

# 2. Rimuove i volumi residui che potrebbero avere lock sul database
docker volume prune -f

# Sequenza finale di reset semplificata ed efficace
# Dovrebbe essere sufficiente uno solo dei comandi di pulizia
# ma per sicurezza possiamo eseguirle tutti e tre (down -v, rm , prune)
docker compose down -v
docker rm -f $(docker ps -aq) 2>/dev/null || true
docker system prune -f --volumes
docker compose up -d
docker compose logs airflow-webserver
```

