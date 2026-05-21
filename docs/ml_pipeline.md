Per iniziare a lavorare, attivare l'ambiente nel terminale con:
source .venv/bin/activate

Per visualizzare help in linea digitare
./setup.sh
----------------------------------------------------
1. Verifica Python 
Python 3.12.1
----------------------------------------------------
HELP IN LINEA
1 -> setup.sh --init  (inizializza progetto , install. librerie/venv) 
2 -> setup.sh --change  (modifica struttura progetto , installazione nuove librerie) 
3 -> setup.sh --install  (installazione librerie tramite requirements.txt) 
4 -> setup.sh --checks  (controllo GPU/CPU verifica installazione librerie) 
5 -> source .venv/bin/activate per attivare l'ambiente virtuale
6 -> deactivate per disattivare l'ambiente virtuale
7 -> ruff check file.py controllo superficiale di un file python
8 -> cd src + PYTHONPATH=. pylint train/file.py per controllo profondo di un file python
9 -> cd src + PYTHONPATH=. python train/train_baseline.py --mode PROD Per avviare in produzione
10-> cd src + PYTHONPATH=. python train/train_baseline.py --mode DEBUG Per avviare in debug(default)
11-> cd src + PYTHONPATH=. python train/train_baseline.py --help per vedere l'help in linea
----------------------------------------------------



Per controllare la correttezza sintattica dei file python

DEBUG MODE
    PARAMETRIZZAZIONE
    NUM_CLASSES: int = 3
    SMALL_TRAIN_DATASET_SIZE: int = 500
    SMALL_VAL_DATASET_SIZE: int = 100
    MAX_LENGTH: int = 64
    SEED: int = 42

    OUTPUT_DIR: str = "./outputs-baseline-debug"
    LEARNING_RATE: float = 2e-5
    BATCH_SIZE: int = 4
    NUM_EPOCHS: int = 1
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 1
    LOGGING_STEPS: int = 5
    EVAL_STRATEGY_MODE: str = "steps"
    SAVE_STRATEGY_MODE: str = "steps"
    REPORT_TO_MODE: str = "mlflow"
    MLFLOW_RUN_NAME: str = "twitter-sentiment-roberta-debug"
    MLFLOW_MODE_RUN: str = "DEBUG"
    MLFLOW_DATASET_TYPE: str = "SMALL"
    MLFLOW_ARTIFACT_PATH: str = "out-model-baseline-debug"

    FLAG_LOAD_BEST_MODEL: bool = True
    FLAG_USE_CPU: bool = True
    MAX_STEPS: int = 20
    FLAG_DEBUG_MODE: bool = True
    FLAG_MONITOR_METRICS: bool = False

    FLAG_DROP_EXPORT_TABLE: bool = True
    FLAG_CREATE_EXPORT_TABLE: bool = True
    METRICS_DB_PATH: str = "metrics_debug.db"

RISULTATI DELLA VERSIONE IN DEBUG MODE:
Il modello senza un training significativo come quello
in debug già riconosce bene frasi
che hanno un sentiment negativo rispetto a quelle positive
mentre dimostra molte difficolta con le frase neutrali
che confonde sopratutto rispetto a quelle negative
come si vede dalla confusion matrix.

Le metriche della funzione di test sono le seguenti:

15:08:47 - INFO - [test_baseline] - eval_loss: 0.8008660674095154
15:08:47 - INFO - [test_baseline] - eval_accuracy: 0.6626506024096386
15:08:47 - INFO - [test_baseline] - eval_f1: 0.637690264957331
15:08:47 - INFO - [test_baseline] - eval_precision: 0.721008532787021
15:08:47 - INFO - [test_baseline] - eval_recall: 0.6626506024096386
15:08:47 - INFO - [test_baseline] - eval_runtime: 700.3498
15:08:47 - INFO - [test_baseline] - eval_samples_per_second: 17.54
15:08:47 - INFO - [test_baseline] - eval_steps_per_second: 4.385
15:08:47 - INFO - [test_baseline] - epoch: 0.16



