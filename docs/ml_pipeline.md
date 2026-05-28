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

OTTIMIZZAZIONE DEGLI HIPERPARAMETRI IN PRODUZIONE
num_epoch da 1 in debug a 2 in produzione
max_length da 128 a 64 e dopo l'analisis statistica a 48

max_length nella sentiment analysis non è “obbligatorio”, ma è uno dei pochi parametri che su modelli tipo RoBERTa ha un impatto molto grande su velocità, memoria e anche qualità.

Ti spiego il perché in modo concreto.

1. Il problema vero: il costo cresce in modo quadratico

I transformer (RoBERTa inclusa) hanno self-attention, che costa:

O(n
2
)

dove n = max_length (numero di token).

Quindi:

raddoppi max_length → il tempo non raddoppia → quadruplica circa
da 128 → 256 token = ~4× più lento
da 256 → 512 token = ~16× più pesante

Su CPU (come la tua) questo è enorme.

2. Effetto su CPU (il tuo caso)

Con 4 core CPU:

max_length alto = CPU sempre al 100% + training lento
batch size alto + max_length alto = RAM saturata + swap (catastrofico)

Quindi su CPU, max_length è spesso il vero collo di bottiglia #1, più del batch size.

3. Effetto sulla qualità (importante ma spesso sopravvalutato)

Nella sentiment analysis:

la maggior parte delle frasi utili sta nei primi 128 token
spesso il modello “ignora” la fine se il testo è lungo

Esempio:

recensione Amazon lunga 400 parole
il sentiment è quasi sempre espresso nei primi 1–2 paragrafi

👉 quindi aumentare max_length spesso non migliora molto l’accuratezza

4. Quando max_length è davvero importante

Serve aumentarlo solo se:

testi molto lunghi (reviews lunghe, legal, documenti)
il sentiment è distribuito nel testo (non solo all’inizio)
task tipo:
analisi documenti
news sentiment
social post lunghi concatenati
5. Regola pratica (molto utile)
Tipo testo	max_length consigliato
tweet / short text	64
recensioni brevi	128
recensioni Amazon / Yelp	128–256
documenti lunghi	256–512
6. Perché hai notato miglioramenti dopo l’ottimizzazione

Perché hai ridotto:

tempo per forward pass
uso RAM
pressione CPU cache
tempo per batch

👉 quindi hai reso il training “linearmente più efficiente”

7. Conclusione netta per il tuo caso

Con CPU 4 core + 16GB RAM:

👉 max_length = 128 è quasi sempre il sweet spot
👉 scendere a 64 se vuoi velocità massima
👉 salire a 256 solo se hai prove che perdi informazione

Se vuoi, posso aiutarti a fare una cosa ancora più utile:
👉 
analizzare la distribuzione reale dei tuoi token e dirti il max_length ottimale statistico





