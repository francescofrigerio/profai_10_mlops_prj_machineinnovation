                             
                             # MACHINE INNOVATION MONITORING

## 1. MONITORAGGIO CONTINUO `08-monitoring.md`
Il monitoring implementa l'osservabilità del sistema. 

## 2.  Monitoraggio e Osservabilità

Il sistema monitora costantemente le performance del modello (data drift, distribuzione delle predizioni).

## 3.  Stack Tecnologico del monitoraggio
* **Rilevamento metriche:** 
* **Data Source:** Sqlite
* **Visualizzazione:** Grafana

## 4.  Dashboard di Grafana
E' stata configurato una dashboard costituita da due panel:
- panel table che elenca tutte le metriche rilevate (accuracy , precision , recall , f1_score) in ordine secondo il campo timestamp.
- time series table 

In questa versione alpha del sistema sono state mantenute le 
credenziali di default di grafana.
```bash
login admin 
password admin
```

## 5. Link alla Dashboard Live
* **[Grafana Cloud Instance]**(Non disponibile in questa versione)**
* **File metrics.db della Dashboard:** [vedere lo script install_db.sh](../install_db.sh)
* **File JSON della Dashboard:** [dashboard_machine_innovation.json](../monitoring/grafana-provisioning/dashboards/dashboard_machine_innovation.json)
* **File JSON metriche:** [ultima accuracy e f1_score](../monitoring/latest_metrics.json)


## 6.  Screenshot della Dashboard Attuale
Ecco come appare il monitoraggio delle metriche.
Per il commento dei risultati vedere la sezione 10.

![Grafana Dashboard Overview](../images/dashboard_timeseries.png)
![Grafana Dashboard Value](../images/dashboard_table.png)

## 7.  Alerting
Gli alert su Airflow sono impostati per attivare il retraing se:
* L'accuracy è inferiore a **0.7**  oppure f1_score è inferiore a **0.7**.

## 8. Modifiche sull'applicazione Web

8.1 Aggiunta Threshold al panel Table 70

8.2 Creato Overrirde sul field timespace con name = time 
(premere sul pulsante show ovveride only)

8.3 Impostato ordinamento sul campo time sul panel table in descending mode. 
L'ordinamento deve essere settato graficamente(freccia verso il basso) in editazione 
cliccando sul campo time del panel di tipo table e prevale
rispetto alla clausola Order by della query.

8.4 Query grafana panel table
8.4.1. il timestamp viene convertito nel formato 
richiesto da Grafana (Unix Epoch in secondi)
8.4.2. nella clausola where viene applicato il filtro temporale nativo di Grafana
Dividendo per 1000 perché Grafana ragiona in millisecondi, 
mentre SQLite (e strftime %s) in secondi

```bash
SELECT CAST(strftime('%s', timestamp) AS INTEGER) AS Data_Train,
  accuracy AS "Accuracy",
  precision AS "Precision",
  recall AS "Recall",
  f1_score AS "F1-Score",
  dom_name as "Mode_Train"
FROM model_metrics_baseline
WHERE CAST(strftime('%s', timestamp) AS INTEGER) >= $__from / 1000 
  AND CAST(strftime('%s', timestamp) AS INTEGER) < $__to / 1000
ORDER BY timestamp ASC
```
Query grafana series table:
8.4.3. nella clausola where viene applicato il filtro temporale nativo di Grafana
Dividendo per 1000 perché Grafana ragiona in millisecondi, 
mentre SQLite (e strftime %s) in secondi
8.4.4. impone che il timestamp sia maggiore o uguale al primo dato storico reale
in modo che il grafico sia visualizzato correttamente
```bash
 SELECT
  accuracy AS "Accuracy",
  precision AS "Precision",
  recall AS "Recall",
  f1_score AS "F1-Score",
FROM model_metrics_baseline
WHERE CAST(strftime('%s', timestamp) AS INTEGER) >= $__from / 1000
  AND CAST(strftime('%s', timestamp) AS INTEGER) < $__to / 1000
  AND timestamp >= (SELECT MIN(timestamp) FROM model_metrics_baseline WHERE accuracy IS NOT NULL)
ORDER BY timestamp ASC  
```


## 9. Manutenzione del sistema
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
sudo lsof -i :3000
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




    