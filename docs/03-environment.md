
                   # MACHINE INNOVATION - ENVIRONMENT

## 1. ENVIRONMENT `03-environment.md`
Questo file descrive i comandi operativi per la creazione
e la manutenzione efficiente dell'environment.

## 2. INIZIALIZZAZIONE DELL'ENVIRONMENT
```bash
./setup --init
```

Viene creata la struttura che a grandi linee è la seguente(output del comando tree).

```bash
tree -L 2
```

```text
.
├── README.md
├── architecture
├── ci_cd
│   ├── CD
│   ├── CI
│   └── Dockerfile
├── docs
│   ├── 01-architecture.md
│   ├── 02-project-overview.md
│   ├── 03-environment.md
│   ├── 04-ml-training.md
│   ├── 05-model-serving.md
│   ├── 06-ci-test.md
│   ├── 07-cicd-train.md
│   ├── 08-monitoring.md
│   ├── 09-scheduling.md
│   └── 10-insights-next-version.md
├── images
│   ├── dashboard_table.png
│   └── dashboard_timeseries.png
├── install_db.sh
├── links
│   ├── Colab_template.txt
│   └── Hugging_Face.txt
├── model_serving
│   ├── Dockerfile
│   ├── README.md
│   ├── __pycache__
│   ├── app.py
│   ├── deploy_space.sh
│   ├── dist_space
│   ├── requirements.txt
│   ├── test_predict_from_app.sh
│   ├── test_predict_from_web.sh
│   ├── train -> ../src/train
│   └── utils -> ../src/utils
├── monitoring
│   ├── all_metrics.json
│   ├── dashboards
│   ├── docker-compose.yaml
│   ├── grafana-provisioning
│   ├── latest_metrics.json
│   └── rend_dashboard_panel.py
├── notebooks
│   ├── profai_10_MLOPS_prj_machineinnovation_v1_eda.ipynb
│   ├── twitter_roberta_base_sentiment_latest_baseline.ipynb
│   └── twitter_roberta_base_sentiment_latest_fine_tuning.ipynb
├── pytest.ini
├── requirements.txt
├── run_mlruns_ui.sh
├── run_pipe_debug.sh
├── run_pipe_prod.sh
├── run_test_ci.sh
├── run_train_debug.sh
├── run_train_prod.sh
├── scheduling
│   ├── config
│   ├── dags
│   ├── docker-compose.yaml
│   ├── logs
│   └── plugins
├── setup.sh
└── src
    ├── __init__.py
    ├── __pycache__
    ├── mlruns
    ├── outputs-baseline-debug
    ├── outputs-baseline-prod
    ├── train
    └── utils
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


2. SCRIPT D'INSTALLAZIONE RESET ENVIRONMENT
```bash
setup.sh --init  # (inizializza progetto , install. librerie/venv) 
setup.sh --change  # (modifica struttura progetto , installazione nuove librerie) 
setup.sh --install  #  (installazione librerie tramite requirements.txt) 
setup.sh --checks  #  (controllo GPU/CPU verifica installazione librerie) 
source .venv/bin/activate #  per attivare l'ambiente virtuale
deactivate #  per disattivare l'ambiente virtuale
ruff check file.py #  controllo superficiale di un file python
cd src ; PYTHONPATH=. pylint train/train_baseline.py #  per controllo profondo di un file python
./run_train_prod.sh #  Training in produzione (--demo per un training demo veloce)
./run_train_debug.sh #  Training in debug(default)
./run_pipe_prod.sh #  Pipeline Inference in produzione
./run_pipe_debug.sh #  Pipeline Inference in debug
```

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

Il seguente comando trova i 10 files che occupano + spazio
``` bash
sudo find / -type f -not -path '*/.git/*' -not -path '/proc/*' -not -path '/sys/*' -exec du -h {} + 2>/dev/null | sort -rh | head -n 10
```

I seguenti comandi cancellano uno dei files elencati
```bash
ls /workspaces/profai_10_mlops_prj_machineinnovation/src/mlruns/
rm -rf 593167092950942131/*
ls /home/codespace/.cache/huggingface/hub/
rm -rf /home/codespace/.cache/huggingface/hub/*

# se abbiamo già salvato il modello da qualche parte
rm -rf /workspaces/profai_10_mlops_prj_machineinnovation/src/outputs-baseline-prod/model_weights/checkpoint-20

pip cache info
pip cache purge
# controllo lo spazio sui diversi file system
du -h --max-depth=1 | sort -hr

```

Ricontrollare occupazione disco sotto il 95%
```bash
df -h /workspaces 
```

Verificare anche la pulizia dei docker container
Può essere lanciato dalla home(non guarda il file docker-compose.yaml)
```bash
docker builder prune -a -f
```

## 7. NOTA PER GITHUB
In caso il comando git push dà il seguente errore :

error: failed to push some refs to 'https://github.com/francescofrigerio/profai_10_mlops_prj_machineinnovation'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.

bisogna eseguire il comando git pull con l'opzione --rebase
```bash
git add .
git commit -m "Il tuo messaggio di commit"

# 2. Scarica le modifiche fatte da GitHub Actions e mettile "sotto" le tue
git pull origin main --rebase

# 3. Ora puoi pushare in tutta sicurezza
git push origin main
```

## 8. Salvare la configurazione del progetto (devcontainer.json)

Nel Codespace, premere F1 (o Ctrl+Shift+P / Cmd+Shift+P).
Cercare e seleziona: Codespaces: Add Dev Container Configuration Files...

Seguire i passaggi per scegliere la configurazione.
Verrà creata una cartella .devcontainer con un file devcontainer.json.

Selezionare Create + Anaconda Python 3 + config container config come unica Additional feature
Per procedere con la creazine dei files sotto .devcontainer premere OK
