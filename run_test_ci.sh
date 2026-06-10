#!/bin/bash

# Interrompe lo script se un comando fallisce
set -e

# Configura il PYTHONPATH sulla cartella corrente per garantire 
# che app.py e i relativi moduli vengano trovati ovunque
export PYTHONPATH=$(pwd):$PYTHONPATH

echo "Avvio di TUTTI i test nella cartella ci_cd/CI/..."

# PASSIAMO LA CARTELLA: Pytest troverà da solo tutti i file test_*.py
python -m pytest ci_cd/CI/ -v -p no:warnings --tb=short

echo "Tutti i file di test sono stati eseguiti!"
