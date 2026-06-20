
                   # MACHINE INNOVATION - ENVIRONMENT

## 1. ENVIRONMENT `02-environment.md`
Questo file descrive i comandi operativi per la creazione
e la manutenzione efficiente dell'environment.

## 2. INIZIALIZZAZIONE DELL'ENVIRONMENT
```bash
./setup --init
```

## 3. RESET DELL'ENVIRONMENT E REINSTALLAZIONE DELLE LIBRERIE
```bash
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip cache purge
pip install --upgrade pip

pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
# oppure
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install -r requirements.txt --no-cache-dir

python -c "import torch; print(torch.__version__)"  # deve stampare 2.x.x+cpu
python -c "import torch; print(torch.cuda.is_available())" # deve dare false
python -c "from transformers import AutoModelForSequenceClassification"
```

## 4. HELP IN LINEA
```bash
./setup.sh
```

## 5. OUTPUT DELL'HELP IN LINEA
1. Verifica Python (max versione 3.12)
Python 3.12.1

2. SCRIPT D'INSTALLAZIONE CONTROLLO MODIFICA E RESET ENVIRONMEN
2.1 -> setup.sh --init  (inizializza progetto , install. librerie/venv) 
2.2 -> setup.sh --change  (modifica struttura progetto , installazione nuove librerie) 
2.3 -> setup.sh --install  (installazione librerie tramite requirements.txt) 
2.4 -> setup.sh --checks  (controllo GPU/CPU verifica installazione librerie) 
2.5 -> source .venv/bin/activate per attivare l'ambiente virtuale
2.6 -> deactivate per disattivare l'ambiente virtuale
2.7 -> ruff check file.py controllo superficiale di un file python
2.8 -> cd src + PYTHONPATH=. pylint train/train_baseline.py per controllo profondo di un file python
2.9 -> ./run_train_prod.sh Training in produzione (--demo per un training demo veloce)
2.10-> ./run_train_debug.sh Training in debug(default)
2.11 -> ./run_pipe_prod.sh Pipeline Inference in produzione
2.12 -> ./run_pipe_debug.sh Pipeline Inference in debug

## 6. PULIZIA DEL DISCO FISSO
Lavorando con sviluppo e test spesso si riempie il disco
del codespace.
Vale la pena in questi casi individuare i 10 files più
pesanti nel workspace e verificare se non sia il caso
di cancellarli.

Il seguente comando segnala occupazione disco sopra il 95%
```bash
df -h /workspaces 
```

Il seguente comando trova i 10 files che occpano + spazio
``` bash
sudo find / -type f -not -path '*/.git/*' -not -path '/proc/*' -not -path '/sys/*' -exec du -h {} + 2>/dev/null | sort -rh | head -n 10
```

I seguenti comandi Cancellano qualcuno dei files elencati
```bash
rm -rf /workspaces/profai_10_mlops_prj_machineinnovation/src/mlruns/593167092950942131/*
rm -rf /home/codespace/.cache/huggingface/hub/*
```

Ricontrollo occupazione disco sotto il 95%
```bash
df -h /workspaces 
```

Verificare anche la pulizia dei docker container
Può essere lanciato dalla home(non guarda il file docker-compose.yaml)
```bash
docker builder prune -a -f
```