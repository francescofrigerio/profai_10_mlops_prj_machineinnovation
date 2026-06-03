#!/bin/bash

# 1. Identifica in modo sicuro la cartella in cui si trova questo script (serving/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 2. Definisce la cartella di output (sotto serving/dist_space)
DIST_DIR="$SCRIPT_DIR/dist_space"

# 3. Definisce la radice del progetto (la cartella superiore a serving/)
ROOT_DIR="$SCRIPT_DIR/.."

echo "Inizio preparazione per il deploy su Hugging Face..."
echo "Cartella di destinazione: $DIST_DIR"

# 4. Pulisce e ricrea la struttura delle cartelle fisiche
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/utils"
mkdir -p "$DIST_DIR/train"

# 5. Copia i file di serving principali (che si trovano in serving/)
cp "$SCRIPT_DIR/app.py" "$DIST_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$DIST_DIR/"

# 6. Copia i file sorgenti reali dalla cartella src/ del progetto
cp "$ROOT_DIR/src/utils/const_baseline.py" "$DIST_DIR/utils/"
cp "$ROOT_DIR/src/utils/utils.py" "$DIST_DIR/utils/"
cp "$ROOT_DIR/src/train/pipe_baseline.py" "$DIST_DIR/train/"

# 7. Crea i file __init__.py vuoti per i moduli Python
touch "$DIST_DIR/utils/__init__.py"
touch "$DIST_DIR/train/__init__.py"

echo "Pronto! Tutti i file fisici reali sono stati copiati e strutturati dentro '$DIST_DIR'."
echo "Ora prendere il contenuto della cartella $DIST_DIR/ e caricarlo su Hugging Face Spaces."