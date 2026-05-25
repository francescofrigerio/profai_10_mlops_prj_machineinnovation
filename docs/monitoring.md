# 1. check main branch is up to date with 'origin/main'
git checkout main
# 2. Create a new branch to run monitoring
git checkout -b monitoring
# 3. At the end of develop the monitoring system Merge Request (o Pull Request) into the main.

Monitoring Reference Guide on https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/

# check docker compose installation
docker compose version
# first go into the directory where you have created this docker-compose.yaml file
cd monitoring

# create the docker-compose.yaml file
touch docker-compose.yaml

# edit yaml file 
services:
  grafana:
    image: grafana/grafana-enterprise
    container_name: grafana
    restart: unless-stopped
    ports:
      - '3000:3000'
    volumes:
      - grafana-storage:/var/lib/grafana
# Use Docker volumes when you want the Docker Engine to manage the storage volume.
# To use Docker volumes for persistent storage,
volumes:
  grafana-storage: {}

# start/stop the grafana container
# d = detached mode
# up = to bring the container up and running
# To determine that Grafana is running, 
# open a browser window and type IP_ADDRESS:3000. The sign in screen should appear.
docker compose up -d
# down = to bring the container down and stopping
docker compose down

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

