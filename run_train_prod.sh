#!/bin/bash

# Valore di default: produzione
MODE="PROD"
OUT_DIR="./src/outputs-baseline-prod"

# Controlla se è stato passato l'argomento --demo o -d
if [[ "$1" == "--demo" || "$1" == "--DEMO" ]]; then
    MODE="DEMO"
    echo "Avvio train in modalità: $MODE PER VELOCIZZARE L'ESECUZIONE"
else
    echo "Avvio train in modalità: $MODE"
fi

# 1. Pulizia checkpoint dedicati alla modalità attiva
rm -rf "${OUT_DIR}/model_weights/checkpoint*"

# 2. Esecuzione del codice Python
cd src || exit
python -m train.train_baseline --mode "$MODE" 2>&1 | tee train_${MODE}.log
cd ..

ls -lrt $OUT_DIR



    
