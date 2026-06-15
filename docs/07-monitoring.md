


./install_db.sh src/outputs-baseline-prod/metrics_prod.db 
Visualizza il seguente output che attesta la copia del db sulla dir di destinazione
=== machineinnovation App: Inizio Installazione Database Metriche ===
[*] Database sorgente individuato: src/outputs-baseline-prod/metrics_prod.db
[*] Configurazione directory di destinazione in /opt/machineinnovation/db...
[V] Directory creata con successo.
[*] Copia del file in corso...
[V] Copia completata: /opt/machineinnovation/db/metrics.db
[*] Configurazione permessi e proprietari...
[V] Permessi configurati correttamente per l'ambiente Linux e Grafana.

=== Installazione Completata con Successo! ===
--------------------------------------------------------
Percorso finale DB:  /opt/machineinnovation/db/metrics.db
Proprietario locale:  codespace
--------------------------------------------------------
[!] Promemoria per Grafana:
Nel pannello di controllo di Grafana, aggiungi un Data Source 'SQLite' e inserisci:
Path: /opt/machineinnovation/db/metrics.db


TEMPLATE FILE README

## 5. `monitoring.md`
L'ultimo file mappa l'osservabilità del sistema. Spiega cosa viene tracciato su Grafana e come accedere alle dashboard.

```markdown
# Monitoraggio e Osservabilità

Il sistema monitora costantemente le performance dell'API (latenza, numero di richieste) e le performance del modello (data drift, distribuzione delle predizioni).

## Stack Tecnologico
* **Rilevamento metriche:** FastAPI Prometheus Instrumentator
* **Data Source:** Prometheus
* **Visualizzazione:** Grafana

## Dashboard di Grafana
Abbiamo configurato una dashboard principale per il controllo della produzione.

* ?? **Link alla Dashboard Live:** [Grafana Cloud Instance](https://tuomonitoring.grafana.net)
* ?? **Backup JSON della Dashboard:** [grafana_dashboard.json](../assets/grafana_dashboard.json)

### Screenshot della Dashboard Attuale
Ecco come appare il monitoraggio del traffico e della latenza di inferenza:

![Grafana Dashboard Overview](../assets/grafana_screenshot.png)

## Alerting
Gli alert sono impostati per attivarsi su Slack se:
* La latenza media supera i **500ms** per più di 5 minuti.
* L'endpoint `/health` restituisce un codice di errore `5xx`.

# tempo link url
http://localhost:3000/goto/bfnbddmmmw1z4d?orgId=1

https://grafana.com/grafana/plugins/grafana-image-renderer/?tab=installation
The Grafana Image Renderer plugin has been deprecated and is no longer maintained by Grafana. Instead, use Grafana Image Renderer remote rendering service.

Use the grafana-cli tool to install Grafana Image Renderer from the commandline:

grafana-cli plugins install grafana-image-renderer
