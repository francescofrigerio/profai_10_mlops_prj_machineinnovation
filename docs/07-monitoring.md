# MACHINE INNOVATION MONITORING

## 1. `monitoring.md`
Il monitoring implementa l'osservabilità del sistema. 
Qui viene spiegato cosa viene tracciato su Grafana e come accedere alle dashboard.

```markdown
# Monitoraggio e Osservabilità

Il sistema monitora costantemente le performance dell'API (latenza, numero di richieste) e le performance del modello (data drift, distribuzione delle predizioni).

## Stack Tecnologico
* **Rilevamento metriche:** FastAPI Machine Innovation
* **Data Source:** Sqlite
* **Visualizzazione:** Grafana

## Dashboard di Grafana
Abbiamo configurato una dashboard principale per il controllo della produzione.

* **Link alla Dashboard Live:** [Grafana Cloud Instance](Non disponibile)
* **Backup JSON della Dashboard:** [grafana_dashboard.json](../monitoring/latest_metrics.json)

### Screenshot della Dashboard Attuale
Ecco come appare il monitoraggio delle metriche:

![Grafana Dashboard Overview](../images/dashboard_timeseries.png)
![Grafana Dashboard Value](../images/dashboard_table.png)

## Alerting
Gli alert su Airflow sono impostati per attivare il retraing se:
* L'accuracy è inferiore a **0.8** .


