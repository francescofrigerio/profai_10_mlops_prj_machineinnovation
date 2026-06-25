                             
                             # MACHINE INNOVATION MONITORING

## 1. `07-monitoring.md`
Il monitoring implementa l'osservabilità del sistema. 
Qui viene spiegato cosa viene tracciato su Grafana e come accedere alle dashboard.

## 2.  Monitoraggio e Osservabilità

Il sistema monitora costantemente le performance dell'API (latenza, numero di richieste) e le performance del modello (data drift, distribuzione delle predizioni).

## 3.  Stack Tecnologico del monitoraggio
* **Rilevamento metriche:** FastAPI Machine Innovation
* **Data Source:** Sqlite
* **Visualizzazione:** Grafana

## 4.  Dashboard di Grafana
Abbiamo configurato una dashboard principale per il controllo della produzione.
Credenziali di default di airflow
login admin 
password admin

* **Link alla Dashboard Live:** [Grafana Cloud Instance](Non disponibile)
* **Backup JSON della Dashboard:** [grafana_dashboard.json](../monitoring/latest_metrics.json)

## 5.  Screenshot della Dashboard Attuale
Ecco come appare il monitoraggio delle metriche:

![Grafana Dashboard Overview](../images/dashboard_timeseries.png)
![Grafana Dashboard Value](../images/dashboard_table.png)

## 6.  Alerting
Gli alert su Airflow sono impostati per attivare il retraing se:
* L'accuracy è inferiore a **0.8** .

## 7. Manutenzione del sistema
Ogni tanto occorre fare pulizia sul disco del codespace e cancellare i vecchi container

Quando si spegne il container cancelliamo il volume
Non perdiamo nulla perchè abbiamo salvato la dashboard
sotto grafana-provisioning e la script install_db.sh
aggiorna il files metrics.db ad ogni esecuzione.
```markdown
docker compose down -v
docker system prune -a --volumes -f
```

# 8. Mancato accesso alla dashboard (admin/admin)
In caso di mancato accesso a grafana sul browser
Ad esempio una verifica sul log potrebbe evidenziare
il lock sul database sqlite.
```markdown
docker logs grafana

# eseguire in ordine e riprovare ad accedere
cd monitoring/
docker compose down -v
docker system prune -f
docker compose up -d
docker logs grafana
```

note path sul file docker-compose.yml
All'avvio: Grafana legge il file di configurazione dentro /etc/... 
(grazie al mount di Docker).

Direttiva: Il file gli dice "Guarda che i tuoi JSON si trovano in /var/lib/grafana/dashboards".

Lettura/Scrittura: Grafana va in quel percorso, che è abilitato alla lettura e alla scrittura. Quando si modifica un grafico e Salviamo, Grafana genera il nuovo JSON e lo scrive in /var/lib/grafana/dashboards.

Sincronizzazione col Codespace: Poiché nel docker-compose.yml hai mappato quella cartella sul tuo file system locale (- ./dashboards:/var/lib/grafana/dashboards), la modifica si riflette all'istante nel Codespace.
```markdown
docker-compose.yml
volumes:
      # Save Grafana data (dashboard, utsers) so we don't loses with reboot
      - grafana-storage:/var/lib/grafana
      # docker compose parte gia' da monitoring come work dir
      # Mappa la cartella del JSON nel Codespace dentro il container di Grafana
      # Sincronizza JSON nel Codespace (./dashboards basato su dove risiede questo file compose)
      - ./dashboards:/var/lib/grafana/dashboards

      - ./grafana-provisioning:/etc/grafana/provisioning
      # mount custom dir host inside Grafana container (ro=read only)
      - /opt/machineinnovation/db:/opt/machineinnovation/db:ro
```

dashboard.yml
```markdown
path: /var/lib/grafana/dashboards
```


Query grafana panel table
SELECT
  -- 1. Converte il timestamp nel formato 
  -- richiesto da Grafana (Unix Epoch in secondi)
  CAST(strftime('%s', timestamp) AS INTEGER) AS Data_Train,
  
  -- 2. Seleziona le metriche da visualizzare sul grafico
  accuracy AS "Accuracy",
  precision AS "Precision",
  recall AS "Recall",
  f1_score AS "F1-Score",
  dom_name as "Mode_Train"

FROM model_metrics_baseline

-- 3. Applica il filtro temporale nativo di Grafana
-- Divide per 1000 perché Grafana ragiona in millisecondi, 
-- mentre SQLite (e strftime %s) in secondi
WHERE CAST(strftime('%s', timestamp) AS INTEGER) >= $__from / 1000 
  AND CAST(strftime('%s', timestamp) AS INTEGER) < $__to / 1000

-- 4. Ordina i dati dal più vecchio al più recente per permettere a Grafana di tirare le linee correttamente
ORDER BY timestamp ASC

Query grafana panel time series
 SELECT
  -- 1. Converte il timestamp nel formato
  -- richiesto da Grafana (Unix Epoch in secondi)
  -- 2. Seleziona le metriche da visualizzare sul grafico
  accuracy AS "Accuracy",
  precision AS "Precision",
  recall AS "Recall",
  f1_score AS "F1-Score",
FROM model_metrics_baseline
-- 3. Applica il filtro temporale nativo di Grafana
-- Divide per 1000 perché Grafana ragiona in millisecondi,
-- mentre SQLite (e strftime %s) in secondi
WHERE CAST(strftime('%s', timestamp) AS INTEGER) >= $__from / 1000
  AND CAST(strftime('%s', timestamp) AS INTEGER) < $__to / 1000
  --AND DOM_NAME in ('train','demo')
  -- impone che il timestamp sia maggiore o uguale al primo dato storico reale
  AND timestamp >= (SELECT MIN(timestamp) FROM model_metrics_baseline WHERE accuracy IS NOT NULL)
-- 4. Ordina i dati dal più vecchio al più recente per permettere a Grafana di tirare le linee correttamente
ORDER BY timestamp ASC      