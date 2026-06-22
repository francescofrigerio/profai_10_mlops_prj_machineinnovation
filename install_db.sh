#!/usr/bin/env bash
# ==============================================================================
# Machine Innovation MLOps Deployment Script - Metrics Database Setup
# ==============================================================================
# Questo script automatizza l'installazione e la centralizzazione del database
# SQLite delle metriche, configurando i permessi corretti per l'integrazione con Grafana.
# ==============================================================================

# Configurazione colori per output leggibili nel terminale
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurazione percorsi predefiniti
DEFAULT_DEBUG_SOURCE_DB="metrics.db"
DEFAULT_SOURCE_DB="metrics.db"
TARGET_DIR="/opt/machineinnovation/db"
TARGET_DB="${TARGET_DIR}/metrics.db"

echo -e "${YELLOW}=== machineinnovation App: Inizio Installazione Database Metriche ===${NC}"

# 1. Controllo se il file sorgente esiste nella directory corrente
if [ ! -f "$DEFAULT_SOURCE_DB" ]; then
    # Cerchiamo se esiste la versione di produzione o se è stato specificato un argomento
    if [ -f "metrics.db" ]; then
        DEFAULT_SOURCE_DB="metrics.db"
        echo -e "${YELLOW}[!] Rilevato database di produzione: ${DEFAULT_SOURCE_DB}${NC}"
    elif [ -n "$1" ] && [ -f "$1" ]; then
        DEFAULT_SOURCE_DB="$1"
    else
        echo -e "${RED}[X] Errore: File database sorgente non trovato!${NC}"
        echo -e "Assicurati di lanciare lo script dalla cartella principale del progetto o specifica il file come argomento:"
        echo -e "Uso: ./install_db.sh [percorso_file_database.db]"
        echo -e "Uso: ./install_db.sh src/outputs-baseline-prod/metrics.db"
        echo -e "Uso: ./install_db.sh src/outputs-baseline-debug/metrics.db"
        exit 1
    fi
fi

echo -e "[*] Database sorgente individuato: ${GREEN}${DEFAULT_SOURCE_DB}${NC}"

# 2. Creazione della struttura delle directory sotto /opt con privilegi sudo
echo -e "[*] Configurazione directory di destinazione in ${TARGET_DIR}..."
if [ ! -d "$TARGET_DIR" ]; then
    sudo mkdir -p "$TARGET_DIR"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[V] Directory creata con successo.${NC}"
    else
        echo -e "${RED}[X] Errore critico nella creazione della directory.${NC}"
        exit 1
    fi
else
    echo -e "[*] Directory di destinazione già esistente."
fi

# 3. Copia del file del database
echo -e "[*] Copia del file in corso..."
sudo cp "$DEFAULT_SOURCE_DB" "$TARGET_DB"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[V] Copia completata: ${TARGET_DB}${NC}"
else
    echo -e "${RED}[X] Errore critico durante la copia del database.${NC}"
    exit 1
fi

# 4. Configurazione avanzata dei permessi per utente corrente e Grafana
echo -e "[*] Configurazione permessi e proprietari..."

# Imposta come proprietario l'utente reale che sta eseguendo lo script (non root) 
# in modo che PyTorch possa continuare ad aggiornarlo liberamente se necessario
REAL_USER=${SUDO_USER:-$USER}
sudo chown -R "${REAL_USER}:${REAL_USER}" /opt/machineinnovation/

# Garantiamo l'accesso in lettura ed esecuzione alle cartelle superiori (cruciale per l'utente 'grafana')
sudo chmod 777 /opt
sudo chmod -R 777 /opt/machineinnovation
sudo chmod -R 777 /opt/machineinnovation/db

# permessi di lettura/scrittura sul file SQLite 
sudo chmod 777 "$TARGET_DB"

echo -e "${GREEN}[V] Permessi configurati correttamente.${NC}"

# 5. Riepilogo e istruzioni finali
echo -e "\n${YELLOW}Installazione Completata con Successo! ${NC}"
echo -e "Percorso finale DB:  ${GREEN}${TARGET_DB}${NC}"
echo -e "Proprietario locale:  ${GREEN}${REAL_USER}${NC}"

ls -lrt $TARGET_DB
echo -e "Installazione db su grafana eseguita con successo"