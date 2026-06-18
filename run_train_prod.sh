#!/bin/bash

# Valore di default: produzione
MODE="PROD"
OUT_DIR="./src/outputs-baseline-prod"

# Controlla se è stato passato l'argomento --demo o -d
if [[ "$1" == "--demo" || "$1" == "--DEMO" ]]; then
    MODE="DEBUG"
    OUT_DIR="./src/outputs-baseline-debug"

    echo "Avvio train in modalità: PROD $MODE PER VELOCIZZARE L'ESECUZIONE"
else
    echo "Avvio train in modalità: $MODE"
fi

# 1. Pulizia checkpoint dedicati alla modalità attiva
rm -rf "${OUT_DIR}/model_weights/checkpoint*"

# 2. Esecuzione del codice Python
cd src || exit
python -m train.train_baseline --mode "$MODE" 2>&1 | tee train_${MODE}.log
cd ..

# in modalità DEBUG, copia gli artefatti in PROD per i test demo
if [ "$MODE" == "DEBUG" ]; then
    echo "Siamo in modalità Demo/Debug: copio gli artefatti in prod..."
    cp ./src/outputs-baseline-debug/metrics.db ./src/outputs-baseline-prod/metrics.db 
    cp ./src/outputs-baseline-debug/roc_curve.png ./src/outputs-baseline-prod/roc_curve.png 
    cp ./src/outputs-baseline-debug/confusion_matrix.png ./src/outputs-baseline-prod/confusion_matrix.png
else
    # Salva i files che potrebbero essere sovrascritti dalla modalita' demo
    cp ./src/outputs-baseline-prod/metrics.db ./src/outputs-baseline-prod/metrics.bak 
    cp ./src/outputs-baseline-prod/roc_curve.png cp ./src/outputs-baseline-prod/roc_curve.bak 
    cp ./src/outputs-baseline-prod/confusion_matrix.png cp ./src/outputs-baseline-prod/confusion_matrix.bak
fi


    
