                 
                 


# MACHINE INNOVATION - ARCHITETTURA

## 1. Schema Architettura `01-architecture.md`

```mermaid
graph TB
    %% Sotto-grafico Airflow
    subgraph AIRFLOW [APACHE AIRFLOW]
        DAG1[DAG: RETRAINING<br>- mode: prod<br>- Mensile ordinario<br>- O su emergenza]
        DAG2[DAG: DAILY MONITORING<br>- mode: prod<br>- Gira OGNI GIORNO<br>- Controlla soglia drift]
        DAG2 -->|Trigger if drift| DAG1
    end

    %% Sotto-grafico GitHub
    subgraph GITHUB [GITHUB REPOSITORY]
        W_RETRAIN[WORKFLOW: RETRAIN<br>- mode: prod/demo<br>- Addestra il modello<br>- Push del nuovo .db]
        W_MONITOR[WORKFLOW: MONITORING<br>- Aggiorna grafici<br>- lettura latest_metrics.json]
        W_MONITOR -->|Scrittura Ultime Metriche| latest_metrics.json
        W_MONITOR -->|Se Ultima Accuracy < 0.8| W_RETRAIN
    end

    %% Elementi Esterni
    HF[HUGGING FACE SPACE<br>- Servizio FastAPI in prod]
    DB[(SQLITE DB<br>- Artefatto del modello
                 <br>- Metriche
                 <br>- Performance)]

    %% Connessioni e Flussi
    DAG1 -->|Chiamata API workflow_dispatch| W_RETRAIN
    DAG2 -->|Chiamata API Estrae JSON| W_MONITOR
    
    W_RETRAIN -->|Deploy automatico| HF
    W_RETRAIN -->|Metriche di output| DB
    W_MONITOR -->|Lettura Ultime Metriche| DB
    DB -->|Legge dati reali| W_MONITOR

    %% Stili grafici
    style AIRFLOW fill:#f9f9f9,stroke:#333,stroke-width:2px
    style GITHUB fill:#f5f5f5,stroke:#333,stroke-width:2px
    style HF fill:#fff5e6,stroke:#ff9900,stroke-width:2px
    style DB fill:#e6f2ff,stroke:#0066cc,stroke-width:2px
```   


 


## 2. DESCRIZIONE ARCHITETTURA E WORKFLOW

                                WORKFLOW RETRAIN AUTOMATICO (mode=prod/demo default=prod)
Esecuzione solo con workflow_dispatch (manuale o attivato da Airflow).
Il riaddestramento di un modello di Machine Learning è un'operazione costosa in termini di tempo e risorse (computazione, GPU, ecc.). Non deve mai scattare in automatico a ogni push.
Pertanto nel workflow CI-CD è stato aggiunta l'esecuzione manuale/automatico del job train separato da test e deploy.

                               WORKFLOW MONITORING CONTINUO (mode=prod/demo default=prod)
Esecuzioe con push su main, manuale (workflow_dispatch), o schedulato da Airflow.
Questo workflow fa un git commit e git push automatico dei grafici e delle metriche sul main, tenerlo isolato sul push del main evita i "loop" infiniti di esecuzione. 
Il dag giornaliero di Airflow lo chiama per leggere l'ultimo valore di Accuracy del sistema e confrontarlo con la soglia = 0.7 . Un valore più appropriato sarebbe 0.8 ma allo stato attuale bisogna stare su un valore di soglia più basso per non far scattare il retrain troppo spesso. Le specifiche attuali non prevedono di ottimizzare le metriche per cui si è preferito curare il funzionamento generale del sistema MLOps. Tuttavia nelle prossime versioni si potranno seguire le indicazione della sezione insights per migliorare le prestazioni.

                              WORKFLOW CI-CD CONTINUO
Viene eseguito ad ogni modifica (sia push che pull_request).
Deve girare sempre per assicurarsi che nessuno rompa il codice.


                              WORKFLOW CI MANUALE
Eseguito solo in manuale tramite workflow_dispatch in modo da non diventare 
ridondante rispetto al flusso CI CD ma rimane visibile nella scheda "Actions" di GitHub sul branch main, pronto per essere testato manualmente all'occorrenza.

                             ORCHESTRAZIONE WORKFLOW CON AIRFLOW
Airflow viene usato come orchestratore per il retraining (basato su una pianificazione mensile o sul rilevamento di data drift giornaliero). Airflow chiama le API di GitHub per attivare il workflow(retrain automatico e/o monitoraggio) tramite il workflow_dispatch.
Vedere la sezione dedicata alla schedulazione per i dettagli.

                             RIEPILOGO
I workflow interagiscono con i seguenti steps:
STEP1: Airflow esegue mensilmente un Retrain automatico (tramite API).
        Il Retrain genera il nuovo file metrics.db contenente accuracy , precision , recall ,f1_score e timestamp. Viene eseguito il push del file metrics.db roc_curve.png confusion_matrix.png

STEP2: Il push attiva il Test Deploy per validare l'integrità del sistema.

STEP3: Se i test passano, il Monitoring si attiva, aggiorna i grafici di Grafana, 
       scatta gli screenshot e consolida la dashboard.
