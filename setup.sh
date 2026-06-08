#!/bin/bash

# Interrompe lo script al primo errore
set -e

# Funzione per i controlli ordinari (GPU, Python, ecc.)
run_help() {
    echo "----------------------------------------------------"
    echo "HELP IN LINEA :  cd src + PYTHONPATH=. python --help"
    echo "1 -> setup.sh --init  (inizializza progetto , install. librerie/venv) "
    echo "2 -> setup.sh --change  (modifica struttura progetto , installazione nuove librerie) "
    echo "3 -> setup.sh --install  (installazione librerie tramite requirements.txt) "
    echo "4 -> setup.sh --checks  (controllo GPU/CPU verifica installazione librerie) "
    echo "5 -> source .venv/bin/activate per attivare l'ambiente virtuale"
    echo "6 -> deactivate per disattivare l'ambiente virtuale"
    echo "7 -> ruff check file.py controllo superficiale di un file python"
    echo "8 -> cd src + PYTHONPATH=. pylint train/train_baseline.py per controllo profondo di un file python"
    echo "9 -> ./train_prod.sh Training in produzione"
    echo "10-> ./train_debug.sh Training in debug(default)"
    echo "11 -> ./pipe_prod.sh Pipeline Inference in produzione"
    echo "Tweet: I love this ProfAi MLOps course! @HuggingFace http://example.com "
    echo "Risultato: [{'label': 'positive', 'score': 0.9962100982666016, 'sentiment': 'positive'}] "

    echo "Comandi docker:"
    echo "docker compose up -d"
    echo "docker compose down"
    echo "docker system prune -a --volumes -f"

    echo "Attenzione!! comandi per pulire ambiente e ricrearlo (da eseguire solo se necessario)"
    echo "pip cache purge"
    echo "deactivate"
    echo "rm -rf .venv"
    echo "python3 -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install --upgrade pip"
    echo "pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir"
    echo "pip install -r requirements.txt --no-cache-dir"

    echo "----------------------------------------------------"
}

run_checks() {
    echo "----------------------------------------------------"
    echo "Verifica Ambiente e Hardware "
    if [ -d ".venv" ]; then
        echo "Visualizzazione pacchetti installati:"
        .venv/bin/pip list | grep -E "torch|transformers|fastapi|mlflow|uvicorn|requests|pydantic|pylint|ruff" || true
        echo "----------------------------------------------------"
        echo "Verifica GPU/CPU via PyTorch:"
        .venv/bin/python -c "import torch; print('GPU Disponibile:', torch.cuda.is_available()); print('Nome GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Nessuna GPU. Uso CPU')"
        
        echo "Verifica compatibilita' tra torch e torchvision:"
        echo "torchvision non e' utilizzato in NLP ma viene richiesto che sia installato da torch"
        .venv/bin/python -c "import torchvision; print(torchvision.__version__)"
        .venv/bin/python -c "import torch; print(torch.__version__)"

    else
        echo "[ERRORE] Ambiente virtuale .venv non trovato. Lancia lo script con il flag --init"
        exit 1
    fi
    echo "----------------------------------------------------"
    echo "Per iniziare a lavorare, attiva l'ambiente nel tuo terminale con:"
    echo "source .venv/bin/activate"
    echo "----------------------------------------------------"
}

echo "----------------------------------------------------"
echo "1. Verifica Python (max versione 3.12)"
python3 --version

# Controllo del parametro in ingresso
if [ "$1" == "--init" ]; then
    echo "----------------------------------------------------"
    echo "INIZIALIZZAZIONE PROGETTO "
    
    # Crea file iniziali nella root se non esistono
    touch .gitignore README.md Dockerfile
    echo -e ".venv/\n__pycache__/\n*.pyc\nmodel/\n.ipynb_checkpoints/" > .gitignore

    echo "2. Creazione della Struttura delle Directory e File"

     # Cartella src/ e relative sottocartelle/file
     # codice per ciclo ML training test evaluate
    mkdir -p src/train src/utils
    touch src/train/train.py   # script con training models
    touch src/train/pipeline.py # pipeline preprocessing+train+validation+test+evaluate
    touch src/train/metrics.py # validazione delle metriche 
    touch src/utils/.gitkeep
    
    # Cartella app/ e relative sottocartelle/file
    # mkdir -p app/routes app/services app/utils
    mkdir -p model_serving/train model_serving/utils
    touch model_serving/app.py
    
    cd model_serving
    ln -s ../src/utils utils
    ln -s ../src/train train
    cd ..

  
    # Cartella tests/ e sottocartelle
    mkdir -p tests/CI tests/CD
    touch tests/CI/.gitkeep
    touch tests/CD/.gitkeep

    # Cartella model/ e file
    mkdir -p model
    # touch model/model.pkl

    # Altre cartelle principali
    mkdir -p airflow monitoring architecture notebooks images
    
    touch monitoring/.gitkeep
    touch images/.gitkeep
    touch airflow/.gitkeep
    touch architecture/.gitkeep
    touch notebooks/.gitkeep

    # cartella per github actions
    mkdir -p .github/workflows
    touch .github/workflows/update-graphs.yml

    # Cartella docs/ e relativi file markdown
    mkdir -p docs
    touch docs/architecture.md
    touch docs/ml_pipeline.md
    touch docs/monitoring.md
    touch docs/deployment.md
    touch docs/api_reference.md

    # Cartella links/ e relativi file
    mkdir -p links
    touch links/Hugging_Face.txt
    touch links/Grafana_screenshots.txt
    touch links/Colab_demo.txt

    echo "Struttura del progetto creata con successo."

    echo "3. Creazione Ambiente Virtuale"
    # Crea l'ambiente virtuale se non esiste già
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "Ambiente virtuale creato con successo."
    else
        echo "L'ambiente virtuale esiste già."
    fi

    echo "4. Installazione Pacchetti"
    # Aggiorna pip all'interno dell'ambiente virtuale
    .venv/bin/pip install --upgrade pip

    # Installa le librerie richieste nel virtualenv
    # .venv/bin/pip install numpy pandas matplotlib mlflow transformers datasets accelerate evaluate scikit-learn torch
    # Installa PyTorch ottimizzato per CUDA 12.1 e poi le altre librerie
    # .venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cu121
    # .venv/bin/pip install transformers datasets accelerate evaluate scikit-learn mlflow 
    .venv/bin/pip install numpy pandas matplotlib seaborn
    .venv/bin/pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
    .venv/bin/pip install --no-cache-dir transformers datasets accelerate evaluate scikit-learn mlflow
    # .venv/bin/pip uninstall fastapi uvicorn requests pydantic
    # sudo du -h -x --max-depth=2 /workspaces 2>/dev/null | sort -hr | head -n 20
    # git gc --prune=now --aggressive
    # sudo find /workspaces -type f -size +50M -exec ls -lh {} + 2>/dev/null | sort -k5 -hr
    
    .venv/bin/pip install pylint ruff
    .venv/bin/pip install playwright
    .venv/bin/pip install --with-deps chromium

    # !pylint test_code.py
    # !ruff check test_code.py

    # echo "5. Generazione requirements.txt"
    # .venv/bin/pip freeze > requirements.txt
    # cat requirements.txt
    # Per la tua pipeline CI/CD, io non fisserei mai nel repository 
    # tutti i 150 pacchetti usciti da pip freeze. 
    # Mantieni solo le dipendenze dirette del progetto. 
    # Le dipendenze transitive (aiohttp, greenlet, graphql-core, ecc.) 
    # lasciale gestire a pip, altrimenti ogni ricostruzione dell'ambiente 
    # diventa fragile e difficile da mantenere.

    
    echo "Elenco pacchetti installati"
    .venv/bin/pip list

    echo "----------------------------------------------------"
    echo " Setup completato con successo!"
    echo " Controlli sul codespaces"
    echo " nvidia-smi"
    echo " Per iniziare a lavorare, attiva l'ambiente virtuale con:"
    echo " source .venv/bin/activate"
    echo " start verifica GPU/CPU"
    # echo " python -c 'import torch; print('GPU Disponibile:', torch.cuda.is_available()); print('Nome GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Nessuna Gpu.Usa CPU')"
    echo ' python -c "import torch; print('\''GPU Disponibile:'\'', torch.cuda.is_available()); print('\''Nome GPU:'\'', torch.cuda.get_device_name(0) if torch.cuda.is_available() else '\''Nessuna GPU. Usa CPU'\'')"'
    echo " end verifica GPU/CPU"
    echo "----------------------------------------------------"
    
    # controllo GPU e stato ambiente
    run_checks
    echo "----------------------------------------------------"
    
elif [ "$1" == "--change" ]; then
    echo "----------------------------------------------------"
    echo "MODIFICA STRUTTURA PROGETTO "
    echo "----------------------------------------------------"
elif [ "$1" == "--install" ]; then
    echo "In caso servisse ripartire da zero eseguire"
    echo "python3 -m venv .venv"
    echo "source .venv/bin/activate"
    echo ".venv/bin/pip install --upgrade pip"
    echo "----------------------------------------------------"
    echo "INSTALLAZIONE LIBRERIE PROGETTO "
    # Per installare le lib dal file requirements nell'ambiente virtuale
    .venv/bin/pip install -r requirements.txt
    echo "----------------------------------------------------"
elif [ "$1" == "--checks" ]; then
    run_checks
else
    # controllo GPU e stato ambiente
    run_help
fi

